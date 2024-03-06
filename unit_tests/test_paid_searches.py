import datetime
import json

from flask import url_for
from flask_testing import TestCase
from mock import patch
from search_local_land_charge_api import main
from search_local_land_charge_api.models import PaidSearch
from unit_tests.data.mock_paid_searches import (
    MOCK_ANONYMOUS_PAID_SEARCH_PAYLOAD,
    MOCK_PAID_SEARCH_MISSING_SEARCH_ID_PAYLOAD, MOCK_PAID_SEARCH_PAYLOAD,
    MOCK_PAID_SEARCHES)


class TestPaidSearches(TestCase):

    def create_app(self):
        main.app.testing = True
        return main.app

    @patch('search_local_land_charge_api.resources.paid_searches.PaidSearch')
    @patch('search_local_land_charge_api.app.validate')
    def test_get_paid_search(self, mock_validate, mock_paid_search):

        mock_paid_search.query.filter.return_value.\
            filter.return_value.\
            order_by.return_value.\
            all.return_value = [MOCK_PAID_SEARCHES['1']]

        response = self.client.get(url_for("paid_searches.get_paid_search_for_user", user_id="test-user-id",
                                           search_id="test-search-id"),
                                   headers={'Authorization': 'Fake JWT'})
        response_data = response.data.decode()

        self.assertStatus(response, 200)
        self.assertIn('"search-id": 1', response_data)
        self.assertIn('"user-id": "test-user-id"', response_data)
        self.assertIn('"payment-id": "test-payment-id"', response_data)
        self.assertIn('"document-url": "test-url"', response_data)
        self.assertIn('"reference": "abc"', response_data)

    @patch('search_local_land_charge_api.resources.paid_searches.PaidSearch')
    @patch('search_local_land_charge_api.app.validate')
    def test_get_paid_search_no_results(self, mock_validate, mock_paid_search):

        mock_paid_search.query.filter.return_value. \
            filter.return_value. \
            order_by.return_value. \
            all.return_value = None

        response = self.client.get(url_for("paid_searches.get_paid_search_for_user", user_id="test-user-id",
                                           search_id="test-search-id"),
                                   headers={'Authorization': 'Fake JWT'})

        self.assertStatus(response, 404)
        self.assertIn("Paid search with id (test-search-id) not found for user with id (test-user-id)",
                      response.data.decode())

    @patch('search_local_land_charge_api.resources.paid_searches.PaidSearch')
    @patch('search_local_land_charge_api.app.validate')
    def test_get_paid_search_by_id(self, mock_validate, mock_paid_search):

        mock_paid_search.query. \
            filter.return_value. \
            order_by.return_value. \
            all.return_value = [MOCK_PAID_SEARCHES['1']]

        response = self.client.get(url_for("paid_searches.get_paid_search_by_id", search_id="test-search-id"),
                                   headers={'Authorization': 'Fake JWT'})
        response_data = response.data.decode()

        self.assertStatus(response, 200)
        self.assertIn('"search-id": 1', response_data)
        self.assertIn('"user-id": "test-user-id"', response_data)
        self.assertIn('"payment-id": "test-payment-id"', response_data)
        self.assertIn('"document-url": "test-url"', response_data)
        self.assertIn('"reference": "abc"', response_data)

    @patch('search_local_land_charge_api.resources.paid_searches.PaidSearch')
    @patch('search_local_land_charge_api.app.validate')
    def test_get_paid_search_by_id_no_results(self, mock_validate, mock_paid_search):

        mock_paid_search.query. \
            filter.return_value. \
            order_by.return_value. \
            all.return_value = None

        response = self.client.get(url_for("paid_searches.get_paid_search_by_id", search_id="test-search-id"),
                                   headers={'Authorization': 'Fake JWT'})

        self.assertStatus(response, 404)
        self.assertIn("Paid search with id (test-search-id) not found",
                      response.data.decode())

    @patch('search_local_land_charge_api.resources.paid_searches.PaidSearch')
    @patch('search_local_land_charge_api.app.validate')
    def test_get_paid_search_by_reference(self, mock_validate, mock_paid_search):

        mock_paid_search.query. \
            filter.return_value. \
            order_by.return_value. \
            all.return_value = [MOCK_PAID_SEARCHES['1']]

        response = self.client.get(url_for("paid_searches.get_paid_search_by_reference", reference="test-search-id"),
                                   headers={'Authorization': 'Fake JWT'})
        response_data = response.data.decode()

        self.assertStatus(response, 200)
        self.assertIn('"search-id": 1', response_data)
        self.assertIn('"user-id": "test-user-id"', response_data)
        self.assertIn('"payment-id": "test-payment-id"', response_data)
        self.assertIn('"document-url": "test-url"', response_data)
        self.assertIn('"reference": "abc"', response_data)

    @patch('search_local_land_charge_api.resources.paid_searches.PaidSearch')
    @patch('search_local_land_charge_api.app.validate')
    def test_get_paid_search_by_reference_no_results(self, mock_validate, mock_paid_search):

        mock_paid_search.query. \
            filter.return_value. \
            order_by.return_value. \
            all.return_value = None

        response = self.client.get(url_for("paid_searches.get_paid_search_by_reference", reference="test-search-id"),
                                   headers={'Authorization': 'Fake JWT'})

        self.assertStatus(response, 404)
        self.assertIn("Paid search with reference (test-search-id) not found",
                      response.data.decode())

    @patch('search_local_land_charge_api.resources.paid_searches.PaidSearch')
    @patch('search_local_land_charge_api.app.validate')
    def test_get_paid_searches(self, mock_validate, mock_paid_search):

        paid_searches = [MOCK_PAID_SEARCHES['1'], MOCK_PAID_SEARCHES['2']]

        mock_paid_search.query.filter.return_value. \
            order_by.return_value. \
            all.return_value = paid_searches

        response = self.client.get(url_for("paid_searches.get_paid_searches_for_user", user_id="test-user-id"),
                                   headers={'Authorization': 'Fake JWT'})
        response_data = response.data.decode()

        self.assertStatus(response, 200)
        self.assertIn('"search-id": 1', response_data)
        self.assertIn('"search-id": 2', response_data)

    @patch('search_local_land_charge_api.resources.paid_searches.PaidSearch')
    @patch('search_local_land_charge_api.app.validate')
    def test_get_paid_searches_no_results(self, mock_validate, mock_paid_search):
        mock_paid_search.query.filter.return_value. \
            order_by.return_value. \
            all.return_value = None

        response = self.client.get(url_for("paid_searches.get_paid_searches_for_user", user_id="test-user-id"),
                                   headers={'Authorization': 'Fake JWT'})

        self.assertStatus(response, 404)
        self.assertIn("No paid searches for user with id (test-user-id)", response.data.decode())

    @patch('search_local_land_charge_api.resources.paid_searches.PaidSearch.query')
    @patch('search_local_land_charge_api.resources.paid_searches.db')
    @patch('search_local_land_charge_api.app.validate')
    def test_save_paid_search_successful(self, mock_validate, mock_db, mock_paid_search):
        response = self.client.post(url_for("paid_searches.save_paid_search", user_id="test-user-id"),
                                    data=json.dumps(MOCK_PAID_SEARCH_PAYLOAD),
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})
        response_data = response.data.decode()

        self.assertStatus(response, 201)
        self.assertIn('"search-id": 1', response_data)
        self.assertIn('"user-id": "test-user-id"', response_data)
        self.assertIn('"payment-id": "test-payment-id"', response_data)
        self.assertIn('"document-url": "test-url"', response_data)
        self.assertIn('"reference": "abc"', response_data)

    @patch('search_local_land_charge_api.resources.paid_searches.PaidSearch.query')
    @patch('search_local_land_charge_api.resources.paid_searches.db')
    @patch('search_local_land_charge_api.app.validate')
    def test_save_paid_search_claimed_successful(self, mock_validate, mock_db, mock_paid_search):

        response = PaidSearch(search_id=1, user_id=None,
                              payment_id="test-payment-id", charges=[],
                              search_extent={"test": "extent"}, search_date=datetime.datetime.now(),
                              document_url="test-url", search_area_description='abc',
                              amount=10, card_brand="test_card", reference="abc", payment_provider="test_provider")

        mock_paid_search.filter.return_value.first.return_value = response

        response = self.client.post(url_for("paid_searches.save_paid_search", user_id="test-user-id"),
                                    data=json.dumps(MOCK_PAID_SEARCH_PAYLOAD),
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})
        response_data = response.data.decode()

        self.assertStatus(response, 201)
        self.assertIn('"search-id": 1', response_data)
        self.assertIn('"user-id": "test-user-id"', response_data)
        self.assertIn('"payment-id": "test-payment-id"', response_data)
        self.assertIn('"document-url": "test-url"', response_data)
        self.assertIn('"reference": "abc"', response_data)
        self.assertIn('"payment-provider": "test_provider"', response_data)
        self.assertIn('"card-brand": "test_card"', response_data)
        self.assertIn('"amount": 10', response_data)
        mock_db.session.commit.assert_called()
        mock_db.session.add.assert_not_called()

    @patch('search_local_land_charge_api.resources.paid_searches.PaidSearch.query')
    @patch('search_local_land_charge_api.resources.paid_searches.db')
    @patch('search_local_land_charge_api.app.validate')
    def test_save_paid_search_update_doc_url(self, mock_validate, mock_db, mock_paid_search):

        response = PaidSearch(search_id=1, user_id=None,
                              payment_id="test-payment-id", charges=[],
                              search_extent={"test": "extent"}, search_date=datetime.datetime.now(),
                              document_url=None, search_area_description='abc',
                              amount=10, card_brand="test_card", reference="abc", payment_provider="test_provider")

        mock_paid_search.filter.return_value.first.return_value = response

        response = self.client.post(url_for("paid_searches.save_paid_search", user_id="test-user-id"),
                                    data=json.dumps(MOCK_PAID_SEARCH_PAYLOAD),
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})
        response_data = response.data.decode()

        self.assertStatus(response, 201)
        self.assertIn('"search-id": 1', response_data)
        self.assertIn('"user-id": "test-user-id"', response_data)
        self.assertIn('"payment-id": "test-payment-id"', response_data)
        self.assertIn('"document-url": "test-url"', response_data)
        self.assertIn('"reference": "abc"', response_data)
        self.assertIn('"payment-provider": "test_provider"', response_data)
        self.assertIn('"card-brand": "test_card"', response_data)
        self.assertIn('"amount": 10', response_data)
        mock_db.session.commit.assert_called()
        mock_db.session.add.assert_not_called()

    @patch('search_local_land_charge_api.resources.paid_searches.db')
    @patch('search_local_land_charge_api.app.validate')
    def test_save_paid_search_invalid_payload(self, mock_validate, mock_db):
        response = self.client.post(url_for("paid_searches.save_paid_search", user_id="test-user-id"),
                                    data=json.dumps(MOCK_PAID_SEARCH_MISSING_SEARCH_ID_PAYLOAD),
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 500)
        self.assertIn("Missing data for required field", response.data.decode())

    @patch('search_local_land_charge_api.app.validate')
    def test_save_paid_failed_user_mismatch(self, mock_validate):
        response = self.client.post(url_for("paid_searches.save_paid_search", user_id="false_user"),
                                    data=json.dumps(MOCK_PAID_SEARCH_PAYLOAD),
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 400)

    @patch('search_local_land_charge_api.resources.paid_searches.PaidSearch.query')
    @patch('search_local_land_charge_api.resources.paid_searches.db')
    @patch('search_local_land_charge_api.app.validate')
    def test_save_paid_search_successful_anonymous(self, mock_validate, mock_db, mock_paid_search):
        response = self.client.post(url_for("paid_searches.save_paid_search", user_id='anonymous'),
                                    data=json.dumps(MOCK_ANONYMOUS_PAID_SEARCH_PAYLOAD),
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})
        response_data = response.data.decode()

        self.assertStatus(response, 201)
        self.assertIn('"search-id": 1', response_data)
        self.assertIn('"user-id": null', response_data)
        self.assertIn('"payment-id": "test-payment-id"', response_data)
        self.assertIn('"document-url": "test-url"', response_data)
        self.assertIn('"reference": "abc"', response_data)
