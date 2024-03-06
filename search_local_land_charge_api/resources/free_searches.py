import json
import uuid
from datetime import datetime
from threading import Thread

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from flask import Blueprint, Response, current_app, g, request
from marshmallow import ValidationError
from search_local_land_charge_api.dependencies.account_api import AccountApi
from search_local_land_charge_api.dependencies.storage_api_service import \
    StorageAPIService
from search_local_land_charge_api.exceptions import ApplicationError
from search_local_land_charge_api.extensions import db
from search_local_land_charge_api.models import FreeSearch, SearchQuery
from search_local_land_charge_api.schema.free_search_schema import \
    FreeSearchSchema
from search_local_land_charge_api.schema.search_query_schema import \
    SearchQuerySchema
from search_local_land_charge_api.utilities.process_geometry import \
    process_geometry
from sqlalchemy import func
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm.session import sessionmaker

free_searches_bp = Blueprint('free_searches', __name__, url_prefix='/free-searches')


@free_searches_bp.route('', methods=['POST'])
def post_free_search():
    """Post free search

    Returns the free search stored
    """

    free_search_json = request.get_json()

    if free_search_json:
        schema = FreeSearchSchema()

        try:
            free_search = schema.load(free_search_json)
        except ValidationError as exc:
            current_app.logger.error("Failed to save free search item: {}".format(exc.normalized_messages()))
            raise ApplicationError(exc.normalized_messages(), "FS002", 400)

        if isinstance(free_search, FreeSearch):
            db.session.add(free_search)
            db.session.commit()
            return Response(schema.dumps(free_search), 201, mimetype='application/json')

    raise ApplicationError("Free search details must be provided in json format", "FS001", 400)


@free_searches_bp.route('/<free_search_id>', methods=['GET'])
def get_free_search(free_search_id):
    """Get free search

    Returns the free search
    """

    free_search = FreeSearch.query.filter_by(_id=free_search_id).first_or_404()
    schema = FreeSearchSchema()

    return Response(schema.dumps(free_search), 200, mimetype='application/json')


@free_searches_bp.route("/query", methods=['POST'])
def post_free_search_query():
    """Query free searches with some parameters"""

    current_app.logger.info("Endpoint called, retrieving data based on supplied parameters")

    request_json = request.get_json()

    if not request_json:
        raise ApplicationError('The request body was invalid', "FS003", 400)

    start_timestamp = request_json.get('start_timestamp')
    end_timestamp = request_json.get('end_timestamp')
    extent = request_json.get('extent')
    customer_id = request_json.get('customer_id')
    uuid = request_json.get('uuid')
    exclude_ids = request_json.get('exclude_ids', [])

    user_id = None
    if uuid:
        user_id = uuid
    elif customer_id:
        user_id = customer_id

    if not (start_timestamp and end_timestamp):
        raise ApplicationError('The request body was invalid', "FS004", 400)

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
        search_query_obj.id, start_datetime, end_datetime, extent, user_id, exclude_ids, session,
        current_app.config['SEARCH_QUERY_TIMEOUT'], current_app.config['SEARCH_QUERY_BUCKET'], current_app.logger,
        g.requests), daemon=True)
    query_thread.start()

    db.session.commit()

    return SearchQuerySchema().dumps(search_query_obj), 202, \
        {"Content-Type": "application/json"}


def search_query(id, start_datetime, end_datetime, extent, user_id, exclude_ids, session, timeout, bucket, logger,
                 requests):
    logger.info("Starting search query")

    try:
        # prevent query taking too long
        session.connection().execute("SET statement_timeout={}".format(timeout * 1000))
        if extent:
            search_geom = process_geometry(extent)
            if user_id:
                free_searches = session.query(FreeSearch) \
                    .filter(func.ST_DWithin(FreeSearch.search_geom, search_geom, 0)) \
                    .filter(FreeSearch.user_id == user_id) \
                    .filter(FreeSearch.search_date >= start_datetime) \
                    .filter(FreeSearch.search_date <= end_datetime) \
                    .order_by(FreeSearch.search_date).all()
            else:
                free_searches = session.query(FreeSearch) \
                    .filter(func.ST_DWithin(FreeSearch.search_geom, search_geom, 0)) \
                    .filter(FreeSearch.search_date >= start_datetime) \
                    .filter(FreeSearch.search_date <= end_datetime) \
                    .filter(FreeSearch.user_id.notin_(exclude_ids)) \
                    .order_by(FreeSearch.search_date).all()
        else:
            if user_id:
                free_searches = session.query(FreeSearch) \
                    .filter(FreeSearch.user_id == user_id) \
                    .filter(FreeSearch.search_date >= start_datetime) \
                    .filter(FreeSearch.search_date <= end_datetime) \
                    .order_by(FreeSearch.search_date).all()
            else:
                free_searches = session.query(FreeSearch) \
                    .filter(FreeSearch.search_date >= start_datetime) \
                    .filter(FreeSearch.search_date <= end_datetime) \
                    .filter(FreeSearch.user_id.notin_(exclude_ids)) \
                    .order_by(FreeSearch.search_date).all()

        logger.info("Results containing '{}' free searches".format(len(free_searches)))

        schema = FreeSearchSchema(many=True)

        searches = schema.dump(free_searches)

        logger.info("Looking up email addresses")

        get_search_emails(searches, logger, requests)

        logger.info("Storing results")

        storage_result = StorageAPIService.save_files(
            {'file': (uuid.uuid4().hex + ".json", json.dumps(searches),
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


@free_searches_bp.route("/query/<query_id>", methods=['GET'])
def get_free_search_query(query_id):
    current_app.logger.info("Querying for query {}".format(query_id))

    search_query_request_result = SearchQuery.query.filter(SearchQuery.id == query_id).one_or_none()

    if not search_query_request_result:
        raise ApplicationError("Search request not found", None, 404)

    return SearchQuerySchema().dumps(search_query_request_result), 200, \
        {"Content-Type": "application/json"}


@free_searches_bp.route("/user_id/<user_id>", methods=['GET'])
def get_free_searches_for_user(user_id):
    end_datetime = datetime.utcnow()
    start_datetime = end_datetime - relativedelta(months=6)
    page_size = int(request.args.get('per_page'))
    page_number = int(request.args.get('page'))

    free_searches_query = FreeSearch.query \
        .filter(FreeSearch.user_id == user_id) \
        .filter(FreeSearch.search_date >= start_datetime) \
        .filter(FreeSearch.search_date <= end_datetime) \
        .order_by(FreeSearch._id.desc())

    result = free_searches_query.paginate(page=page_number, per_page=page_size)

    return {
        "items": [FreeSearchSchema().dump(free_search) for free_search in result.items],
        "total": result.total,
        "pages": result.pages
    }


@free_searches_bp.route("/user_id/<user_id>/<search_id>", methods=['GET'])
def get_free_searche_for_user_using_search_id(user_id, search_id):
    end_datetime = datetime.utcnow()
    start_datetime = end_datetime - relativedelta(months=6)

    free_searches_query = FreeSearch.query \
        .filter(FreeSearch._id == search_id) \
        .filter(FreeSearch.user_id == user_id) \
        .filter(FreeSearch.search_date >= start_datetime) \
        .filter(FreeSearch.search_date <= end_datetime)

    result = free_searches_query.all()

    if not result:
        return f"Free search with id ({search_id}) not found", 404

    return Response(json.dumps(FreeSearchSchema().dump(result[0])), 200, mimetype='application/json')


def get_search_emails(searches, logger, requests):
    user_info_cache = {}
    for search in searches:
        userid = search.get('user-id')
        if userid and userid != 'anonymous':
            if userid not in user_info_cache:
                user_info_cache[userid] = AccountApi.get_user(userid, logger, requests)
            user_info = user_info_cache[userid]
            if user_info:
                search['email'] = user_info.get('email')
            else:
                search['email'] = None
        else:
            search['email'] = 'anonymous'
