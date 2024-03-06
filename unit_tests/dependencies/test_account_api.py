from unittest.mock import MagicMock

from flask import g
from flask_testing import TestCase
from search_local_land_charge_api import main
from search_local_land_charge_api.dependencies.account_api import AccountApi
from search_local_land_charge_api.exceptions import ApplicationError


class TestAccountApi(TestCase):

    def create_app(self):
        main.app.testing = True
        return main.app

    def test_get_user_404(self):
        with main.app.app_context():
            with main.app.test_request_context():
                mock_response = MagicMock()
                mock_response.status_code = 404
                g.trace_id = "An ID"
                g.requests = MagicMock()
                g.requests.get.return_value = mock_response
                account_api = AccountApi()
                result = account_api.get_user("anuser")
                self.assertIsNone(result)

    def test_get_user_500(self):
        with main.app.app_context():
            with main.app.test_request_context():
                mock_response = MagicMock()
                mock_response.status_code = 500
                g.trace_id = "An ID"
                g.requests = MagicMock()
                g.requests.get.return_value = mock_response
                account_api = AccountApi()
                with self.assertRaises(ApplicationError):
                    account_api.get_user("anuser")

    def test_get_user_ok(self):
        with main.app.app_context():
            with main.app.test_request_context():
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"some": "response"}
                g.requests = MagicMock()
                g.requests.get.return_value = mock_response
                account_api = AccountApi()
                g.trace_id = "An ID"
                result = account_api.get_user("anuser")
                self.assertEqual(result, {"some": "response"})

    def test_get_inactive_users_404(self):
        with main.app.app_context():
            with main.app.test_request_context():
                mock_response = MagicMock()
                mock_response.status_code = 404
                mock_response.json.return_value = []
                g.trace_id = "An ID"
                g.requests = MagicMock()
                g.requests.get.return_value = mock_response
                account_api = AccountApi()
                result = account_api.get_inactive_users("12")
                self.assertEqual(result, [])

    def test_get_inactive_users_500(self):
        with main.app.app_context():
            with main.app.test_request_context():
                mock_response = MagicMock()
                mock_response.status_code = 500
                g.trace_id = "An ID"
                g.requests = MagicMock()
                g.requests.get.return_value = mock_response
                account_api = AccountApi()
                with self.assertRaises(ApplicationError):
                    account_api.get_inactive_users("12")

    def test_get_inactive_users_ok(self):
        with main.app.app_context():
            with main.app.test_request_context():
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"some": "response"}
                g.trace_id = "An ID"
                g.requests = MagicMock()
                g.requests.get.return_value = mock_response
                account_api = AccountApi()
                result = account_api.get_inactive_users("12")
                self.assertEqual(result, {"some": "response"})

    def test_remove_user_404(self):
        with main.app.app_context():
            with main.app.test_request_context():
                mock_response = MagicMock()
                mock_response.status_code = 404
                mock_response.json.return_value = []
                g.trace_id = "An ID"
                g.requests = MagicMock()
                g.requests.delete.return_value = mock_response
                account_api = AccountApi()
                with self.assertRaises(ApplicationError):
                    account_api.remove_user("dave")

    def test_remove_user_500(self):
        with main.app.app_context():
            with main.app.test_request_context():
                mock_response = MagicMock()
                mock_response.status_code = 500
                g.trace_id = "An ID"
                g.requests = MagicMock()
                g.requests.delete.return_value = mock_response
                account_api = AccountApi()
                with self.assertRaises(ApplicationError):
                    account_api.remove_user("dave")

    def test_remove_user_ok(self):
        with main.app.app_context():
            with main.app.test_request_context():
                mock_response = MagicMock()
                mock_response.status_code = 204
                g.trace_id = "An ID"
                g.requests = MagicMock()
                g.requests.delete.return_value = mock_response
                account_api = AccountApi()
                account_api.remove_user("dave")
                g.requests.delete.assert_called()
