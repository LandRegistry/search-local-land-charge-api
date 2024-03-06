# Command line entry point for deleting inactive users

import argparse
import uuid

from flask import current_app, g
from search_local_land_charge_api import config
from search_local_land_charge_api.app import RequestsSessionTimeout, app
from search_local_land_charge_api.dependencies.account_api import AccountApi
from search_local_land_charge_api.dependencies.authentication_api import \
    AuthenticationApiService
from search_local_land_charge_api.dependencies.report_api import ReportApi
from search_local_land_charge_api.extensions import register_extensions

parser = argparse.ArgumentParser(description='Deletes inactive users')

parser.add_argument('-m', '--months', dest='months',
                    help='months of inactivity',
                    metavar='', default=None, required=True)

parser.add_argument('-a', '--auth-url', dest='auth_url',
                    help='URL of authentication-api, defaults to {}'.format(config.AUTHENTICATION_API_URL),
                    metavar='', default=config.AUTHENTICATION_API_URL)

parser.add_argument('-k', '--api-key', dest='api_key',
                    help='api key to authorise access with',
                    metavar='', required=True)

args = parser.parse_args()

config.AUTHENTICATION_API_URL = args.auth_url

# Get an app and request context so all the bits behind the scenes work
with app.app_context():

    with app.test_request_context():

        g.trace_id = uuid.uuid4().hex
        g.requests = RequestsSessionTimeout()

        register_extensions(app)

        current_app.logger.info('Inactive user removal job started')
        current_app.logger.info("Removing inactive users with parameters: {}".format(str(args)))

        if not args.months:
            current_app.logger.error("Incorrect months entered")
            exit(1)

        parameters = {}

        int_jwt = AuthenticationApiService.get_anonymous_jwt(args.api_key)

        if not int_jwt:
            current_app.logger.error("Internal JWT not generated")
            exit(1)

        g.requests.headers.update({'X-Trace-ID': g.trace_id})
        g.requests.headers.update(
            {'Authorization': 'Bearer ' + int_jwt})

        try:
            # Get list of inactive users
            inactive_users = AccountApi.get_inactive_users(args.months)
            for user in inactive_users:
                current_app.logger.info("Removing user {}".format(user['id']))
                AccountApi.remove_user(user['id'])
                current_app.logger.info("Removed user {}".format(user['id']))
            ReportApi.send_event("inactive_users", {"user_count": len(inactive_users)})
        except Exception as exc:
            current_app.logger.error("Inactive users failed to be removed: {}".format(repr(exc)))
            exit(1)

        current_app.logger.info("Inactive users removed successfully")
