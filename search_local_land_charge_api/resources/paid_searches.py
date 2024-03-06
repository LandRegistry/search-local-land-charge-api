from flask import Blueprint, Response, current_app, json, request
from marshmallow import ValidationError
from search_local_land_charge_api.exceptions import ApplicationError
from search_local_land_charge_api.extensions import db
from search_local_land_charge_api.mapper.paid_search_response_mapper import \
    map_paid_search_response
from search_local_land_charge_api.models import PaidSearch
from search_local_land_charge_api.schema.paid_search_schema import \
    PaidSearchSchema
from sqlalchemy import func, or_

paid_searches_bp = Blueprint('paid_searches', __name__, url_prefix='/users')


@paid_searches_bp.route('/<user_id>/paid-searches/<search_id>', methods=['GET'])
def get_paid_search_for_user(user_id, search_id):
    """Get paid search by ID for a particular user

    Returns the paid search item with search_id for a user with user_id
    """

    paid_searches_query = PaidSearch.query \
        .filter(PaidSearch.user_id == user_id) \
        .filter(or_(PaidSearch.search_id == search_id, PaidSearch.parent_search_id == search_id)) \
        .order_by(PaidSearch.search_date.desc())

    paid_searches = paid_searches_query.all()

    if not paid_searches:
        return "Paid search with id ({}) not found for user with id ({})".format(search_id, user_id), 404

    mapped_paid_searches = map_paid_search_response(paid_searches)

    if mapped_paid_searches:
        return Response(json.dumps(mapped_paid_searches[0]), 200, mimetype='application/json')
    else:
        raise ApplicationError("Something went wrong mapping response object for {}".format(search_id), 500)


@paid_searches_bp.route('/paid-searches/<search_id>', methods=['GET'])
def get_paid_search_by_id(search_id):
    """Get paid search by ID

    Returns the paid search item with search_id
    """
    paid_searches_query = PaidSearch.query \
        .filter(PaidSearch.search_id == search_id) \
        .order_by(PaidSearch.search_date.desc())

    paid_searches = paid_searches_query.all()

    if not paid_searches:
        return "Paid search with id ({}) not found".format(search_id), 404

    mapped_paid_searches = map_paid_search_response(paid_searches)

    if mapped_paid_searches:
        return Response(json.dumps(mapped_paid_searches[0]), 200, mimetype='application/json')
    else:
        raise ApplicationError("Something went wrong mapping response object for {}".format(search_id), 500)


@paid_searches_bp.route('/payments/<reference>', methods=['GET'])
def get_paid_search_by_reference(reference):
    """Get paid search by reference

    Returns the paid search item with reference
    """
    paid_searches_query = PaidSearch.query \
        .filter(func.upper(PaidSearch.reference) == reference.upper()) \
        .order_by(PaidSearch.search_date)

    paid_searches = paid_searches_query.all()

    if not paid_searches:
        return "Paid search with reference ({}) not found".format(reference), 404

    mapped_paid_searches = map_paid_search_response(paid_searches)

    if mapped_paid_searches:
        return Response(json.dumps(mapped_paid_searches[0]), 200, mimetype='application/json')
    else:
        raise ApplicationError("Something went wrong mapping response object for {}".format(reference), 500)


@paid_searches_bp.route('/<user_id>/paid-searches', methods=['GET'])
def get_paid_searches_for_user(user_id):
    """Get all paid searches for a particular user

    Returns all associated paid search items for a user with user_id
    """

    paid_searches_query = PaidSearch.query \
        .filter(PaidSearch.user_id == user_id) \
        .order_by(PaidSearch.search_date.desc())

    paid_searches = paid_searches_query.all()

    if not paid_searches:
        return "No paid searches for user with id ({})".format(user_id), 404

    mapped_paid_searches = map_paid_search_response(paid_searches)

    if mapped_paid_searches:
        return Response(json.dumps(mapped_paid_searches), 200, mimetype='application/json')
    else:
        raise ApplicationError("Something went wrong mapping response object for {}".format(user_id), 500)


@paid_searches_bp.route('/<user_id>/paid-searches', methods=['POST'])
def save_paid_search(user_id):
    """Save paid search item into search history table

    Returns created paid search item for user_id
    """
    paid_search_json = request.get_json()

    if paid_search_json:
        schema = PaidSearchSchema()

        try:
            paid_search = schema.load(paid_search_json)
        except ValidationError as exc:
            current_app.logger.error("Failed to save paid search item: {}".format(exc.normalized_messages()))
            return "{}".format(exc.normalized_messages()), 500

        if user_id != 'anonymous' and user_id != paid_search.user_id:
            current_app.logger.error("Failed to save paid search item: invalid user id in payload")
            return "Failed to save paid search item: invalid user id in payload", 400

        if isinstance(paid_search, PaidSearch):
            existing_search = PaidSearch.query.filter(PaidSearch.search_id == paid_search.search_id).first()
            if existing_search is not None:
                if existing_search.payment_id == paid_search.payment_id:
                    if existing_search.user_id is None:
                        existing_search.user_id = paid_search.user_id
                    if existing_search.document_url is None:
                        existing_search.document_url = paid_search.document_url
                    db.session.commit()
                    return Response(schema.dumps(paid_search), 201, mimetype='application/json')

            db.session.add(paid_search)
            db.session.commit()
            return Response(schema.dumps(paid_search), 201, mimetype='application/json')
