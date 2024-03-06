from unittest.mock import MagicMock

from flask import g
from flask_testing import TestCase
from search_local_land_charge_api import main
from search_local_land_charge_api.dependencies.authentication_api import \
    AuthenticationApiService
from search_local_land_charge_api.exceptions import ApplicationError


class TestAuthenticationApi(TestCase):

    def create_app(self):
        main.app.testing = True
        return main.app

    def test_get_user_500(self):
        with main.app.app_context():
            with main.app.test_request_context():
                mock_response = MagicMock()
                mock_response.status_code = 500
                g.trace_id = "An ID"
                g.requests = MagicMock()
                g.requests.post.return_value = mock_response
                authentication_api = AuthenticationApiService()
                with self.assertRaises(ApplicationError):
                    authentication_api.get_anonymous_jwt("ankey")
                g.requests.post.assert_called()

    def test_get_user_ok(self):
        with main.app.app_context():
            with main.app.test_request_context():
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.text = "anjwt"
                g.trace_id = "An ID"
                g.requests = MagicMock()
                g.requests.post.return_value = mock_response
                authentication_api = AuthenticationApiService()
                result = authentication_api.get_anonymous_jwt("ankey")
                self.assertEqual(result, "anjwt")
                g.requests.post.assert_called()
