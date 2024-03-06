from flask import current_app, g
from search_local_land_charge_api.config import ACCOUNT_API_URL
from search_local_land_charge_api.exceptions import ApplicationError


class AccountApi(object):
    """Class for making requests to Account API endpoints."""

    @staticmethod
    def get_user(user_id, logger=None, requests=None):
        if not logger:
            logger = current_app.logger
        if not requests:
            requests = g.requests

        url = ACCOUNT_API_URL + '/v1.0/users/' + user_id
        logger.info("Calling Account API at {}".format(url))
        response = requests.get(url)

        if response.status_code == 404:
            logger.warning("User id '{}' not found".format(user_id))
            return None
        elif response.status_code != 200:
            logger.error("Error retrieving user")
            raise ApplicationError("Error retrieving user", "AC01", response.status_code)

        logger.info("Successfully retrieved user")

        return response.json()

    @staticmethod
    def get_inactive_users(months):

        url = current_app.config['ACCOUNT_API_URL'] + '/v1.0/users/inactive'
        current_app.logger.info("Calling Account API at {}".format(url))
        response = g.requests.get(url, params={"months": months})

        if response.status_code == 404:
            current_app.logger.warning("No inactive users found")
        elif response.status_code != 200:
            current_app.logger.error("Error retrieving user")
            raise ApplicationError("Error retrieving user", "AC02", response.status_code)

        current_app.logger.info("Successfully retrieved users")

        return response.json()

    @staticmethod
    def remove_user(user_id):

        url = current_app.config['ACCOUNT_API_URL'] + '/v1.0/users/' + user_id
        current_app.logger.info("Calling Account API at {}".format(url))
        response = g.requests.delete(url, params={"nuke": "true"})

        if response.status_code == 404:
            current_app.logger.warning("No user '{}' found".format(user_id))
            raise ApplicationError("Error removing user", "AC03", response.status_code)
        elif response.status_code != 204:
            current_app.logger.error("Error removing user")
            raise ApplicationError("Error removing user", "AC04", response.status_code)

        current_app.logger.info("Successfully removed user")
