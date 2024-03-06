import json
import logging
import sys
from datetime import datetime
from unittest.mock import ANY, MagicMock

from flask import url_for
from flask_testing import TestCase
from mock import patch
from search_local_land_charge_api import main
from search_local_land_charge_api.exceptions import ApplicationError
from search_local_land_charge_api.resources.search_status_searches import \
    search_query

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


class TestSearchStatusSearches(TestCase):

    def create_app(self):
        main.app.testing = True
        self.maxDiff = None
        return main.app

    @patch('search_local_land_charge_api.resources.search_status_searches.db')
    @patch('search_local_land_charge_api.app.validate')
    def test_post_search_status_search_ok(self, mock_validate, mock_db):

        mock_payload = {"display_name": "adisplayname",
                        "charge_ids": ["LLC-1", "LLC-2", "LLC-3", "LLC-4"],
                        "search_extent": POLYGON_FC,
                        "search_date": datetime.utcnow().isoformat(),
                        "organisation": "anorganisation"}

        response = self.client.post(url_for("search_status_searches.post_search_status_search"),
                                    headers={'Authorization': 'Fake JWT',
                                             'Content-type': 'application/json'},
                                    data=json.dumps(mock_payload))
        response_data = json.loads(response.data.decode())
        self.assertEqual(response_data, mock_payload)
        self.assertStatus(response, 201)

    @patch('search_local_land_charge_api.resources.search_status_searches.db')
    @patch('search_local_land_charge_api.app.validate')
    def test_post_search_status_search_errors(self, mock_validate, mock_db):

        mock_payload = {"display_name": "adisplayname",
                        "charge_ids": ["LLC-1", "LLC-2", "LLC-3", "LLC-4"],
                        "search_extent": POLYGON_FC,
                        "organisation": "anorganisation"}

        response = self.client.post(url_for("search_status_searches.post_search_status_search"),
                                    headers={'Authorization': 'Fake JWT',
                                             'Content-type': 'application/json'},
                                    data=json.dumps(mock_payload))
        response_data = json.loads(response.data.decode())
        self.assertEqual(response_data, {'error_code': 'SSS002', 'error_message': {
                         'search_date': ['Missing data for required field.']}})
        self.assertStatus(response, 400)

    @patch('search_local_land_charge_api.resources.search_status_searches.db')
    @patch('search_local_land_charge_api.app.validate')
    def test_post_search_status_search_no_json(self, mock_validate, mock_db):

        mock_payload = {}
        response = self.client.post(url_for("search_status_searches.post_search_status_search"),
                                    headers={'Authorization': 'Fake JWT',
                                             'Content-type': 'application/json'},
                                    data=json.dumps(mock_payload))
        self.assertStatus(response, 400)

    @patch('search_local_land_charge_api.app.validate')
    def test_post_search_status_search_query_nojson(self, mock_validate):
        response = self.client.post(url_for("search_status_searches.post_search_status_search_query"),
                                    headers={'Authorization': 'Fake JWT',
                                             'Content-type': 'application/json'},
                                    json={})
        self.assertStatus(response, 400)

    @patch('search_local_land_charge_api.app.validate')
    def test_post_search_status_search_query_nodates(self, mock_validate):
        response = self.client.post(url_for("search_status_searches.post_search_status_search_query"),
                                    headers={'Authorization': 'Fake JWT',
                                             'Content-type': 'application/json'},
                                    json={"extent": POLYGON_FC,
                                          "uuid": "anuuid",
                                          "exclude_ids": ["anid"]})
        self.assertStatus(response, 400)

    @patch('search_local_land_charge_api.app.validate')
    @patch('search_local_land_charge_api.resources.search_status_searches.Thread')
    @patch('search_local_land_charge_api.resources.search_status_searches.db')
    def test_post_search_status_search_query_ok(self, mock_db, mock_thread, mock_validate):
        response = self.client.post(url_for("search_status_searches.post_search_status_search_query"),
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
        mock_thread.assert_called_with(target=ANY, args=(None, ANY, ANY, POLYGON_FC, ANY, ANY, 'llcs-search-query',
                                                         ANY, ANY), daemon=True)
        self.assertStatus(response, 202)

    @patch('search_local_land_charge_api.resources.search_status_searches.db')
    def test_search_query_exception_no_query(self, mock_db):

        mock_session = MagicMock()
        mock_session.connection.side_effect = [Exception("An exception")]
        mock_logger = MagicMock()
        mock_db.session = mock_session
        mock_session.query.return_value.filter.return_value.one_or_none.return_value = None

        with self.assertRaises(ApplicationError):
            search_query("id", "start_datetime", "end_datetime", "extent", mock_session,
                         "timeout", "bucket", mock_logger, "requests")
        mock_session.connection.assert_called()
        mock_session.query.return_value.filter.return_value.one_or_none.assert_called()
        mock_session.rollback.assert_called()
        mock_session.close.assert_called()

    @patch('search_local_land_charge_api.resources.search_status_searches.db')
    def test_search_query_exception_with_query(self, mock_db):

        mock_session = MagicMock()
        mock_session.connection.side_effect = [Exception("An exception")]
        mock_logger = MagicMock()
        mock_db.session = mock_session
        mock_search_query = MagicMock()
        mock_session.query.return_value.filter.return_value.one_or_none.return_value = mock_search_query

        search_query("id", "start_datetime", "end_datetime", "extent", mock_session,
                     "timeout", "bucket", mock_logger, "requests")
        mock_session.connection.assert_called()
        mock_session.query.return_value.filter.return_value.one_or_none.assert_called()
        self.assertEqual(mock_search_query.status, "FAILED")
        mock_session.commit.assert_called()
        mock_session.rollback.assert_called()
        mock_session.close.assert_called()

    @patch('search_local_land_charge_api.resources.search_status_searches.StorageAPIService')
    @patch('search_local_land_charge_api.resources.search_status_searches.SearchStatusSearchSchema')
    @patch('search_local_land_charge_api.resources.search_status_searches.process_geometry')
    def test_search_query_ok_with_extent(self, mock_process_geom, mock_sss_schema,
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

        mock_sss_schema.return_value.dump.return_value = [{"some": "json"}]

        mock_session.query.return_value.filter.return_value.one_or_none.return_value = mock_search_query

        mock_storage.save_files.return_value = mock_storage_result

        search_query("id", "start_datetime", "end_datetime", POLYGON_FC, mock_session,
                     "timeout", "bucket", logger, "requests")
        mock_session.connection.assert_called()
        mock_session.query.return_value.filter.return_value.one_or_none.assert_called()
        mock_session.query.return_value.filter.return_value.filter.return_value.filter.return_value \
                    .order_by.return_value.all.assert_called()
        self.assertEqual(mock_search_query.status, "COMPLETED")
        self.assertEqual(mock_search_query.document, "/areference")
        self.assertEqual(mock_search_query.external_url, "anexternalreference")
        mock_session.commit.assert_called()
        mock_session.rollback.assert_called()
        mock_session.close.assert_called()

    @patch('search_local_land_charge_api.resources.search_status_searches.StorageAPIService')
    @patch('search_local_land_charge_api.resources.search_status_searches.SearchStatusSearchSchema')
    @patch('search_local_land_charge_api.resources.search_status_searches.process_geometry')
    def test_search_query_ok_with_noextent_nouserid(self, mock_process_geom, mock_sss_schema,
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

        mock_sss_schema.return_value.dump.return_value = [{"some": "json"}]

        mock_session.query.return_value.filter.return_value.one_or_none.return_value = mock_search_query

        mock_storage.save_files.return_value = mock_storage_result

        search_query("id", "start_datetime", "end_datetime", None, mock_session,
                     "timeout", "bucket", logger, "requests")
        mock_session.connection.assert_called()
        mock_session.query.return_value.filter.return_value.one_or_none.assert_called()
        mock_session.query.return_value.filter.return_value.filter.return_value \
                    .order_by.return_value.all.assert_called()
        self.assertEqual(mock_search_query.status, "COMPLETED")
        self.assertEqual(mock_search_query.document, "/areference")
        self.assertEqual(mock_search_query.external_url, "anexternalreference")
        mock_session.commit.assert_called()
        mock_session.rollback.assert_called()
        mock_session.close.assert_called()

    @patch('search_local_land_charge_api.resources.search_status_searches.StorageAPIService')
    @patch('search_local_land_charge_api.resources.search_status_searches.SearchStatusSearchSchema')
    @patch('search_local_land_charge_api.resources.search_status_searches.process_geometry')
    def test_search_query_fail_no_query(self, mock_process_geom, mock_sss_schema,
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

        mock_sss_schema.return_value.dump.return_value = [{"some": "json"}]

        mock_session.query.return_value.filter.return_value.one_or_none.return_value = None

        mock_storage.save_files.return_value = mock_storage_result

        with self.assertRaises(ApplicationError):

            search_query("id", "start_datetime", "end_datetime", None, mock_session,
                         "timeout", "bucket", logger, "requests")
            mock_session.connection.assert_called()
            mock_session.query.return_value.filter.return_value.one_or_none.assert_called()
            mock_session.query.return_value.filter.return_value.filter.return_value \
                        .order_by.return_value.all.assert_called()
            mock_session.commit.assert_not_called()
            mock_session.rollback.assert_called()
            mock_session.close.assert_called()

    @patch('search_local_land_charge_api.app.validate')
    @patch('search_local_land_charge_api.resources.search_status_searches.SearchQuery')
    @patch('search_local_land_charge_api.resources.search_status_searches.SearchQuerySchema')
    def test_get_free_search_query_found(self, mock_search_query_schema, mock_search_query, mock_validate):

        mock_search_query_obj = MagicMock()

        mock_search_query.query.filter.return_value.one_or_none.return_value = mock_search_query_obj
        mock_search_query_schema.return_value.dumps.return_value = "Rhubarb"

        response = self.client.get(url_for("search_status_searches.search_status_search_query", query_id=2),
                                   headers={'Authorization': 'Fake JWT'})
        self.assertStatus(response, 200)
        self.assertEqual(response.text, "Rhubarb")
        mock_search_query.query.filter.assert_called()

    @patch('search_local_land_charge_api.app.validate')
    @patch('search_local_land_charge_api.resources.search_status_searches.SearchQuery')
    @patch('search_local_land_charge_api.resources.search_status_searches.SearchQuerySchema')
    def test_get_free_search_query_notfound(self, mock_search_query_schema, mock_search_query, mock_validate):

        mock_search_query.query.filter.return_value.one_or_none.return_value = None
        mock_search_query_schema.return_value.dumps.return_value = "Rhubarb"

        response = self.client.get(url_for("search_status_searches.search_status_search_query", query_id=2),
                                   headers={'Authorization': 'Fake JWT'})
        self.assertStatus(response, 404)
        mock_search_query.query.filter.assert_called()
