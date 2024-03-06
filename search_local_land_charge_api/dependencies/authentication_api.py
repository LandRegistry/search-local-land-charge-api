from flask import current_app, g
from search_local_land_charge_api import config
from search_local_land_charge_api.exceptions import ApplicationError


class AuthenticationApiService(object):

    @staticmethod
    def get_anonymous_jwt(api_key):
        response = g.requests.post("{}/authentication/anonymous".format(config.AUTHENTICATION_API_URL),
                                   data={'source': 'SEARCH'}, headers={'Authorization': "Bearer {}".format(api_key)})
        current_app.logger.debug("authentication-api response: {}".format(response))
        if response.status_code == 200:
            current_app.logger.info("Internal JWT returned successfully.")
            result = response.text
        else:
            current_app.logger.info("Failed get internal JWT.")
            raise ApplicationError("Failed get internal JWT", "AU01", response.status_code)
        return result
