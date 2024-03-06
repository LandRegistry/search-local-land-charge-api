import uuid
from datetime import datetime
from threading import Thread

from dateutil.parser import parse
from flask import Blueprint, Response, current_app, g, request
from marshmallow import ValidationError
from search_local_land_charge_api.dependencies.storage_api_service import \
    StorageAPIService
from search_local_land_charge_api.exceptions import ApplicationError
from search_local_land_charge_api.extensions import db
from search_local_land_charge_api.models import SearchQuery, SearchStatusSearch
from search_local_land_charge_api.schema.search_query_schema import \
    SearchQuerySchema
from search_local_land_charge_api.schema.search_status_search_schema import \
    SearchStatusSearchSchema
from search_local_land_charge_api.utilities.process_geometry import \
    process_geometry
from sqlalchemy import func
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm.session import sessionmaker

search_status_searches_bp = Blueprint('search_status_searches', __name__, url_prefix='/search-status-searches')


@search_status_searches_bp.route('', methods=['POST'])
def post_search_status_search():
    """Post search status search

    Returns the search status search stored
    """

    search_status_search_json = request.get_json()

    if search_status_search_json:
        schema = SearchStatusSearchSchema()

        try:
            search_status_search = schema.load(search_status_search_json)
        except ValidationError as exc:
            current_app.logger.error("Failed to save search status search item: {}".format(exc.normalized_messages()))
            raise ApplicationError(exc.normalized_messages(), "SSS002", 400)

        if isinstance(search_status_search, SearchStatusSearch):
            db.session.add(search_status_search)
            db.session.commit()
            return Response(schema.dumps(search_status_search), 201, mimetype='application/json')

    raise ApplicationError("Search status search details must be provided in json format", "SSS001", 400)


@search_status_searches_bp.route("/query", methods=['POST'])
def post_search_status_search_query():
    """Query search status searches with some parameters"""

    current_app.logger.info("Endpoint called, retrieving data based on supplied parameters")

    request_json = request.get_json()

    if not request_json:
        raise ApplicationError('The request body was invalid', "SSS003", 400)

    start_timestamp = request_json.get('start_timestamp')
    end_timestamp = request_json.get('end_timestamp')
    extent = request_json.get('extent')

    if not (start_timestamp and end_timestamp):
        raise ApplicationError('The request body was invalid', "SSS004", 400)

    start_datetime = parse(start_timestamp)
    end_datetime = parse(end_timestamp)

    search_query_obj = SearchQuery(datetime.utcnow(), None, g.jwt.principle.principle_id, None, None, "STARTED")
    db.session.add(search_query_obj)
    db.session.flush()
    db.session.refresh(search_query_obj)

    session_factory = sessionmaker(bind=db.engine)
    session = scoped_session(session_factory)

    current_app.logger.info("Querying for charges with filter {}".format(request_json))

    query_thread = Thread(target=search_query, args=(
        search_query_obj.id, start_datetime, end_datetime, extent, session,
        current_app.config['SEARCH_QUERY_TIMEOUT'], current_app.config['SEARCH_QUERY_BUCKET'], current_app.logger,
        g.requests), daemon=True)
    query_thread.start()

    db.session.commit()

    return SearchQuerySchema().dumps(search_query_obj), 202, \
        {"Content-Type": "application/json"}


def search_query(id, start_datetime, end_datetime, extent, session, timeout, bucket, logger, requests):

    logger.info("Starting search query")

    try:
        # prevent query taking too long
        session.connection().execute("SET statement_timeout={}".format(timeout * 1000))

        if extent:
            search_geom = process_geometry(extent)
            search_status_searches = session.query(SearchStatusSearch) \
                .filter(func.ST_DWithin(SearchStatusSearch.search_geom, search_geom, 0)) \
                .filter(SearchStatusSearch.search_date >= start_datetime) \
                .filter(SearchStatusSearch.search_date <= end_datetime) \
                .order_by(SearchStatusSearch.search_date).all()
        else:
            search_status_searches = session.query(SearchStatusSearch) \
                .filter(SearchStatusSearch.search_date >= start_datetime) \
                .filter(SearchStatusSearch.search_date <= end_datetime) \
                .order_by(SearchStatusSearch.search_date).all()

        logger.info("Results containing '{}' searches".format(len(search_status_searches)))
        logger.info("Storing results")

        storage_result = StorageAPIService.save_files(
            {'file': (uuid.uuid4().hex + ".json", SearchStatusSearchSchema(many=True).dumps(search_status_searches),
                      "application/json")}, bucket, logger, requests)

        search_query_obj = session.query(SearchQuery).filter(SearchQuery.id == id).one_or_none()
        if not search_query_obj:
            raise ApplicationError("Search query object not found", None, 500)

        search_query_obj.document = "/" + storage_result['file'][0]['reference']
        search_query_obj.external_url = storage_result['file'][0]['external_reference']
        search_query_obj.completion_timestamp = datetime.utcnow()
        search_query_obj.status = "COMPLETED"

        session.commit()

        logger.info("Results stored")

    except Exception:
        logger.exception("Failed to complete search query")
        search_query_obj = session.query(SearchQuery).filter(SearchQuery.id == id).one_or_none()
        if not search_query_obj:
            raise ApplicationError("Search query object not found", None, 500)

        search_query_obj.completion_timestamp = datetime.utcnow()
        search_query_obj.status = "FAILED"

        session.commit()

    finally:
        session.rollback()
        session.close()


@search_status_searches_bp.route("/query/<query_id>", methods=['GET'])
def search_status_search_query(query_id):
    current_app.logger.info("Querying for query {}".format(query_id))

    search_query_request_result = SearchQuery.query.filter(SearchQuery.id == query_id).one_or_none()

    if not search_query_request_result:
        raise ApplicationError("Search request not found", None, 404)

    return SearchQuerySchema().dumps(search_query_request_result), 200, \
        {"Content-Type": "application/json"}
