import json

from flask import Blueprint, Response
from search_local_land_charge_api.dependencies.account_api import AccountApi
from search_local_land_charge_api.exceptions import ApplicationError

search_service_users_bp = Blueprint('search_service_users', __name__, url_prefix='/users')


@search_service_users_bp.route('/<user_id>', methods=['GET'])
def get_user_info(user_id):
    """Query userid for information

    Returns the userid information
    """

    user_info = AccountApi.get_user(user_id)
    if not user_info:
        raise ApplicationError("User id '{}' not found".format(user_id), "GU01", 404)

    return Response(json.dumps(user_info), 200, mimetype='application/json')
