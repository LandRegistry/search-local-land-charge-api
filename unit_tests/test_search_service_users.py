import json

from flask import url_for
from flask_testing import TestCase
from mock import patch
from search_local_land_charge_api import main


class TestSearchServiceUsers(TestCase):

    def create_app(self):
        main.app.testing = True
        return main.app

    @patch('search_local_land_charge_api.resources.search_service_users.AccountApi')
    @patch('search_local_land_charge_api.app.validate')
    def test_get_user_info_ok(self, mock_validate, mock_accountapi):

        mock_accountapi.get_user.return_value = {"test": "thing"}

        response = self.client.get(url_for("search_service_users.get_user_info", user_id="test"),
                                   headers={'Authorization': 'Fake JWT',
                                            'Content-type': 'application/json'})
        response_data = json.loads(response.data.decode())
        self.assertEqual(response_data, {"test": "thing"})
        self.assertStatus(response, 200)

    @patch('search_local_land_charge_api.resources.search_service_users.AccountApi')
    @patch('search_local_land_charge_api.app.validate')
    def test_get_user_info_notfound(self, mock_validate, mock_accountapi):

        mock_accountapi.get_user.return_value = None

        response = self.client.get(url_for("search_service_users.get_user_info", user_id="test"),
                                   headers={'Authorization': 'Fake JWT',
                                            'Content-type': 'application/json'})
        self.assertStatus(response, 404)
