import json
import logging
import sys
from datetime import datetime, timezone
from unittest.mock import ANY, MagicMock, call

from flask import url_for
from flask_testing import TestCase
from mock import patch
from search_local_land_charge_api import main
from search_local_land_charge_api.exceptions import ApplicationError
from search_local_land_charge_api.models import FreeSearch
from search_local_land_charge_api.resources.free_searches import (
    get_search_emails, search_query)

POLYGON_FC = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {},
            "geometry":
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            0.0,
                            0.0
                        ],
                        [
                            1.0,
                            0.0
                        ],
                        [
                            1.0,
                            1.0
                        ],
                        [
                            0.0,
                            1.0
                        ],
                        [
                            0.0,
                            0.0
                        ]
                    ]
                ]
            }
        }
    ]
}

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class TestFreeSearches(TestCase):

    def create_app(self):
        main.app.testing = True
        return main.app

    @patch('search_local_land_charge_api.resources.free_searches.db')
    @patch('search_local_land_charge_api.app.validate')
    def test_post_free_search_ok(self, mock_validate, mock_db):

        mock_payload = {"user-id": "auser",
                        "charge-ids": [1, 2, 3, 4],
                        "search-extent": POLYGON_FC,
                        "search-date": datetime.now(timezone.utc).isoformat(),
                        "address": "anaddress"}

        response = self.client.post(url_for("free_searches.post_free_search"),
                                    headers={'Authorization': 'Fake JWT',
                                             'Content-type': 'application/json'},
                                    data=json.dumps(mock_payload))
        response_data = json.loads(response.data.decode())
        mock_payload['id'] = None
        self.assertEqual(response_data, mock_payload)
        self.assertStatus(response, 201)

    @patch('search_local_land_charge_api.resources.free_searches.db')
    @patch('search_local_land_charge_api.app.validate')
    def test_post_free_search_errors(self, mock_validate, mock_db):

        mock_payload = {"user-id": "auser",
                        "charge-ids": [1, 2, 3, 4],
                        "search-extent": {"an": "extent"}}

        response = self.client.post(url_for("free_searches.post_free_search"),
                                    headers={'Authorization': 'Fake JWT',
                                             'Content-type': 'application/json'},
                                    data=json.dumps(mock_payload))
        response_data = json.loads(response.data.decode())
        self.assertEqual(response_data, {'error_code': 'FS002', 'error_message': {
                         'search_date': ['Missing data for required field.']}})
        self.assertStatus(response, 400)

    @patch('search_local_land_charge_api.resources.free_searches.db')
    @patch('search_local_land_charge_api.app.validate')
    def test_post_free_search_no_json(self, mock_validate, mock_db):

        mock_payload = {}

        response = self.client.post(url_for("free_searches.post_free_search"),
                                    headers={'Authorization': 'Fake JWT',
                                             'Content-type': 'application/json'},
                                    data=json.dumps(mock_payload))
        self.assertStatus(response, 400)

    @patch('search_local_land_charge_api.app.validate')
    def test_post_free_search_query_nojson(self, mock_validate):
        response = self.client.post(url_for("free_searches.post_free_search_query"),
                                    headers={'Authorization': 'Fake JWT',
                                             'Content-type': 'application/json'},
                                    json={})
        self.assertStatus(response, 400)

    @patch('search_local_land_charge_api.app.validate')
    def test_post_free_search_query_nodates(self, mock_validate):
        response = self.client.post(url_for("free_searches.post_free_search_query"),
                                    headers={'Authorization': 'Fake JWT',
                                             'Content-type': 'application/json'},
                                    json={"extent": POLYGON_FC,
                                          "uuid": "anuuid",
                                          "exclude_ids": ["anid"]})
        self.assertStatus(response, 400)

    @patch('search_local_land_charge_api.app.validate')
    @patch('search_local_land_charge_api.resources.free_searches.Thread')
    @patch('search_local_land_charge_api.resources.free_searches.db')
    def test_post_free_search_query_ok(self, mock_db, mock_thread, mock_validate):
        response = self.client.post(url_for("free_searches.post_free_search_query"),
                                    headers={'Authorization': 'Fake JWT',
                                             'Content-type': 'application/json'},
                                    json={"start_timestamp": "2021-01-01 01:01:01",
                                          "end_timestamp": "2021-01-01 01:01:01",
                                          "extent": POLYGON_FC,
                                          "customer_id": "ancustomer",
                                          "exclude_ids": ["anid"]})
        mock_db.session.add.assert_called()
        mock_db.session.flush.assert_called()
        mock_db.session.refresh.assert_called()
        mock_db.session.commit.assert_called()
        mock_thread.assert_called_with(target=ANY, args=(None, ANY, ANY, POLYGON_FC, 'ancustomer', ['anid'],
                                                         ANY, ANY, ANY, ANY, ANY), daemon=True)
        self.assertStatus(response, 202)

    @patch('search_local_land_charge_api.resources.free_searches.db')
    def test_search_query_exception_no_query(self, mock_db):

        mock_session = MagicMock()
        mock_session.connection.side_effect = [Exception("An exception")]
        mock_logger = MagicMock()
        mock_db.session = mock_session
        mock_session.query.return_value.filter.return_value.one_or_none.return_value = None

        with self.assertRaises(ApplicationError):
            search_query("id", "start_datetime", "end_datetime", "extent", "user_id", "exclude_ids", mock_session,
                         "timeout", "bucket", mock_logger, "requests")
        mock_session.connection.assert_called()
        mock_session.query.return_value.filter.return_value.one_or_none.assert_called()
        mock_session.rollback.assert_called()
        mock_session.close.assert_called()

    @patch('search_local_land_charge_api.resources.free_searches.db')
    def test_search_query_exception_with_query(self, mock_db):

        mock_session = MagicMock()
        mock_session.connection.side_effect = [Exception("An exception")]
        mock_db.session = mock_session
        mock_logger = MagicMock()
        mock_search_query = MagicMock()
        mock_session.query.return_value.filter.return_value.one_or_none.return_value = mock_search_query

        search_query("id", "start_datetime", "end_datetime", "extent", "user_id", "exclude_ids", mock_session,
                     "timeout", "bucket", mock_logger, "requests")
        mock_session.connection.assert_called()
        mock_session.query.return_value.filter.return_value.one_or_none.assert_called()
        self.assertEqual(mock_search_query.status, "FAILED")
        mock_session.commit.assert_called()
        mock_session.rollback.assert_called()
        mock_session.close.assert_called()

    @patch('search_local_land_charge_api.resources.free_searches.StorageAPIService')
    @patch('search_local_land_charge_api.resources.free_searches.get_search_emails')
    @patch('search_local_land_charge_api.resources.free_searches.FreeSearchSchema')
    @patch('search_local_land_charge_api.resources.free_searches.process_geometry')
    def test_search_query_ok_with_extent_userid(self, mock_process_geom, mock_free_schema, mock_emails,
                                                mock_storage):

        mock_session = MagicMock()
        mock_search_query = MagicMock()
        mock_storage_result = {
            'file': [
                {
                    'reference': "areference",
                    'external_reference': "anexternalreference"
                }
            ]
        }

        mock_free_schema.return_value.dump.return_value = [{"some": "json"}]

        mock_session.query.return_value.filter.return_value.one_or_none.return_value = mock_search_query

        mock_storage.save_files.return_value = mock_storage_result

        search_query("id", "start_datetime", "end_datetime", POLYGON_FC, "user_id", None, mock_session,
                     "timeout", "bucket", logger, "requests")
        mock_session.connection.assert_called()
        mock_session.query.return_value.filter.return_value.one_or_none.assert_called()
        mock_session.query.return_value.filter.return_value.filter.return_value.filter.return_value \
                    .filter.return_value.order_by.return_value.all.assert_called()
        self.assertEqual(mock_search_query.status, "COMPLETED")
        self.assertEqual(mock_search_query.document, "/areference")
        self.assertEqual(mock_search_query.external_url, "anexternalreference")
        mock_session.commit.assert_called()
        mock_session.rollback.assert_called()
        mock_session.close.assert_called()

    @patch('search_local_land_charge_api.resources.free_searches.StorageAPIService')
    @patch('search_local_land_charge_api.resources.free_searches.get_search_emails')
    @patch('search_local_land_charge_api.resources.free_searches.FreeSearchSchema')
    @patch('search_local_land_charge_api.resources.free_searches.process_geometry')
    def test_search_query_ok_with_extent_nouserid(self, mock_process_geom, mock_free_schema, mock_emails,
                                                  mock_storage):

        mock_session = MagicMock()
        mock_search_query = MagicMock()
        mock_storage_result = {
            'file': [
                {
                    'reference': "areference",
                    'external_reference': "anexternalreference"
                }
            ]
        }

        mock_free_schema.return_value.dump.return_value = [{"some": "json"}]

        mock_session.query.return_value.filter.return_value.one_or_none.return_value = mock_search_query

        mock_storage.save_files.return_value = mock_storage_result

        search_query("id", "start_datetime", "end_datetime", POLYGON_FC, None, ["exclude_ids"], mock_session,
                     "timeout", "bucket", logger, "requests")
        mock_session.connection.assert_called()
        mock_session.query.return_value.filter.return_value.one_or_none.assert_called()
        self.assertEqual(mock_search_query.status, "COMPLETED")
        self.assertEqual(mock_search_query.document, "/areference")
        self.assertEqual(mock_search_query.external_url, "anexternalreference")
        mock_session.commit.assert_called()
        mock_session.rollback.assert_called()
        mock_session.close.assert_called()

    @patch('search_local_land_charge_api.resources.free_searches.StorageAPIService')
    @patch('search_local_land_charge_api.resources.free_searches.get_search_emails')
    @patch('search_local_land_charge_api.resources.free_searches.FreeSearchSchema')
    @patch('search_local_land_charge_api.resources.free_searches.process_geometry')
    def test_search_query_ok_with_noextent_nouserid(self, mock_process_geom, mock_free_schema, mock_emails,
                                                    mock_storage):

        mock_session = MagicMock()
        mock_search_query = MagicMock()
        mock_storage_result = {
            'file': [
                {
                    'reference': "areference",
                    'external_reference': "anexternalreference"
                }
            ]
        }

        mock_free_schema.return_value.dump.return_value = [{"some": "json"}]

        mock_session.query.return_value.filter.return_value.one_or_none.return_value = mock_search_query

        mock_storage.save_files.return_value = mock_storage_result

        search_query("id", "start_datetime", "end_datetime", None, "user_id", None, mock_session,
                     "timeout", "bucket", logger, "requests")
        mock_session.connection.assert_called()
        mock_session.query.return_value.filter.return_value.one_or_none.assert_called()
        mock_session.query.return_value.filter.return_value.filter.return_value \
                    .filter.return_value.order_by.return_value.all.assert_called()
        self.assertEqual(mock_search_query.status, "COMPLETED")
        self.assertEqual(mock_search_query.document, "/areference")
        self.assertEqual(mock_search_query.external_url, "anexternalreference")
        mock_session.commit.assert_called()
        mock_session.rollback.assert_called()
        mock_session.close.assert_called()

    @patch('search_local_land_charge_api.resources.free_searches.StorageAPIService')
    @patch('search_local_land_charge_api.resources.free_searches.get_search_emails')
    @patch('search_local_land_charge_api.resources.free_searches.FreeSearchSchema')
    @patch('search_local_land_charge_api.resources.free_searches.process_geometry')
    def test_search_query_ok_with_noextent_userid(self, mock_process_geom, mock_free_schema, mock_emails,
                                                  mock_storage):

        mock_session = MagicMock()
        mock_search_query = MagicMock()
        mock_storage_result = {
            'file': [
                {
                    'reference': "areference",
                    'external_reference': "anexternalreference"
                }
            ]
        }

        mock_free_schema.return_value.dump.return_value = [{"some": "json"}]

        mock_session.query.return_value.filter.return_value.one_or_none.return_value = mock_search_query

        mock_storage.save_files.return_value = mock_storage_result

        search_query("id", "start_datetime", "end_datetime", None, None, ["exclude_ids"], mock_session,
                     "timeout", "bucket", logger, "requests")
        mock_session.connection.assert_called()
        mock_session.query.return_value.filter.return_value.one_or_none.assert_called()
        mock_session.query.return_value.filter.return_value.filter.return_value \
                    .filter.return_value.order_by.return_value.all.assert_called()
        self.assertEqual(mock_search_query.status, "COMPLETED")
        self.assertEqual(mock_search_query.document, "/areference")
        self.assertEqual(mock_search_query.external_url, "anexternalreference")
        mock_session.commit.assert_called()
        mock_session.rollback.assert_called()
        mock_session.close.assert_called()

    @patch('search_local_land_charge_api.resources.free_searches.StorageAPIService')
    @patch('search_local_land_charge_api.resources.free_searches.get_search_emails')
    @patch('search_local_land_charge_api.resources.free_searches.FreeSearchSchema')
    @patch('search_local_land_charge_api.resources.free_searches.process_geometry')
    def test_search_query_fail_no_query(self, mock_process_geom, mock_free_schema, mock_emails,
                                        mock_storage):

        mock_session = MagicMock()
        mock_storage_result = {
            'file': [
                {
                    'reference': "areference",
                    'external_reference': "anexternalreference"
                }
            ]
        }

        mock_free_schema.return_value.dump.return_value = [{"some": "json"}]

        mock_session.query.return_value.filter.return_value.one_or_none.return_value = None

        mock_storage.save_files.return_value = mock_storage_result

        with self.assertRaises(ApplicationError):

            search_query("id", "start_datetime", "end_datetime", None, None, ["exclude_ids"], mock_session,
                         "timeout", "bucket", logger, "requests")
            mock_session.connection.assert_called()
            mock_session.query.return_value.filter.return_value.one_or_none.assert_called()
            mock_session.query.return_value.filter.return_value.filter.return_value \
                        .filter.return_value.order_by.return_value.all.assert_called()
            mock_session.commit.assert_not_called()
            mock_session.rollback.assert_called()
            mock_session.close.assert_called()

    @patch('search_local_land_charge_api.app.validate')
    @patch('search_local_land_charge_api.resources.free_searches.SearchQuery')
    @patch('search_local_land_charge_api.resources.free_searches.SearchQuerySchema')
    def test_get_free_search_query_found(self, mock_search_query_schema, mock_search_query, mock_validate):

        mock_search_query_obj = MagicMock()

        mock_search_query.query.filter.return_value.one_or_none.return_value = mock_search_query_obj
        mock_search_query_schema.return_value.dumps.return_value = "Rhubarb"

        response = self.client.get(url_for("free_searches.get_free_search_query", query_id=2),
                                   headers={'Authorization': 'Fake JWT'})
        self.assertStatus(response, 200)
        self.assertEqual(response.text, "Rhubarb")
        mock_search_query.query.filter.assert_called()

    @patch('search_local_land_charge_api.app.validate')
    @patch('search_local_land_charge_api.resources.free_searches.SearchQuery')
    @patch('search_local_land_charge_api.resources.free_searches.SearchQuerySchema')
    def test_get_free_search_query_notfound(self, mock_search_query_schema, mock_search_query, mock_validate):

        mock_search_query.query.filter.return_value.one_or_none.return_value = None
        mock_search_query_schema.return_value.dumps.return_value = "Rhubarb"

        response = self.client.get(url_for("free_searches.get_free_search_query", query_id=2),
                                   headers={'Authorization': 'Fake JWT'})
        self.assertStatus(response, 404)
        mock_search_query.query.filter.assert_called()

    @patch('search_local_land_charge_api.resources.free_searches.AccountApi')
    def test_get_search_emails(self, mock_account_api):
        searches = [
            {"user-id": "userid1"},
            {"user-id": "anonymous"},
            {"user-id": "userid1"},
            {"user-id": "userid2"}
        ]
        mock_account_api.get_user.side_effect = [
            {"email": "userid1email"},
            None
        ]
        mock_logger = MagicMock()
        mock_request = MagicMock()
        get_search_emails(searches, mock_logger, mock_request)

        self.assertEqual(searches[0]['email'], "userid1email")
        self.assertEqual(searches[1]['email'], "anonymous")
        self.assertEqual(searches[2]['email'], "userid1email")
        self.assertEqual(searches[3]['email'], None)
        mock_account_api.get_user.assert_has_calls([call("userid1", mock_logger, mock_request),
                                                    call("userid2", mock_logger, mock_request)])

    @patch('search_local_land_charge_api.app.validate')
    @patch('search_local_land_charge_api.resources.free_searches.FreeSearch')
    @patch('search_local_land_charge_api.resources.free_searches.FreeSearchSchema')
    def test_get_free_search_for_user(self, mock_free_search_schema, mock_free_search, mock_validate):

        mock_paginated = MagicMock()
        mock_paginated.total = 3
        mock_paginated.items = ['item2']
        mock_paginated.pages = 2

        mock_free_search.query.filter.return_value.\
            filter.return_value.\
            filter.return_value.\
            order_by.return_value.paginate.return_value = mock_paginated
        mock_free_search.search_date = datetime.utcnow()
        mock_free_search_schema.return_value.dump.return_value = 'Rhubarb'

        response = self.client.get(url_for('free_searches.get_free_searches_for_user',
                                           user_id='2', page=20, per_page=1),
                                   headers={'Authorization': 'Fake JWT'})
        self.assertStatus(response, 200)
        self.assertEqual(response.json, {'items': ['Rhubarb'], 'pages': 2, 'total': 3})
        mock_free_search.query.filter.assert_called()

    @patch('search_local_land_charge_api.app.validate')
    @patch('search_local_land_charge_api.resources.free_searches.FreeSearch')
    @patch('search_local_land_charge_api.resources.free_searches.FreeSearchSchema')
    def test_get_free_search_using_id_search_exist(self, mock_free_search_schema, mock_free_search, mock_validate):

        mock_free_search.query.filter.return_value.\
            filter.return_value.\
            filter.return_value.\
            filter.return_value.\
            all.return_value = ['Rhubarb']
        mock_free_search.search_date = datetime.utcnow()

        mock_free_search_schema.return_value.dump.return_value = 'Rhubarb'

        response = self.client.get(url_for('free_searches.get_free_searche_for_user_using_search_id', user_id='2',
                                           search_id='1'),
                                   headers={'Authorization': 'Fake JWT'})
        self.assertStatus(response, 200)
        self.assertEqual(response.json, 'Rhubarb')
        mock_free_search.query.filter.assert_called()

    @patch('search_local_land_charge_api.app.validate')
    @patch('search_local_land_charge_api.resources.free_searches.FreeSearch')
    def test_get_free_search_using_id_search_nothing_returned(self, mock_free_search, mock_validate):

        mock_free_search.query.filter.return_value.\
            filter.return_value.\
            filter.return_value.\
            filter.return_value.\
            all.return_value = None
        mock_free_search.search_date = datetime.utcnow()

        response = self.client.get(url_for('free_searches.get_free_searche_for_user_using_search_id', user_id='2',
                                   search_id='1'),
                                   headers={'Authorization': 'Fake JWT'})
        self.assertStatus(response, 404)
        self.assertEqual(response.text, 'Free search with id (1) not found')
        mock_free_search.query.filter.assert_called()

    @patch('search_local_land_charge_api.app.validate')
    @patch('search_local_land_charge_api.resources.free_searches.FreeSearch')
    def test_get_free_search_(self, mock_free_search, mock_validate):
        now_datetime = datetime.now()
        mock_result = FreeSearch("anuserid", [1, 2], POLYGON_FC, now_datetime, "an address")
        mock_free_search.query.filter_by.return_value.first_or_404.return_value = mock_result

        response = self.client.get(url_for("free_searches.get_free_search", free_search_id=1),
                                   headers={'Authorization': 'Fake JWT'})
        self.assertStatus(response, 200)
        self.assertEqual(response.json, {'charge-ids': [1, 2],
                                         'id': None,
                                         'search-date': now_datetime.isoformat(),
                                         'search-extent': POLYGON_FC,
                                         'user-id': 'anuserid',
                                         'address': 'an address'})
