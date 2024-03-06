from datetime import datetime, timezone

from flask import current_app, g
from search_local_land_charge_api.config import REPORT_API_BASE_URL
from search_local_land_charge_api.exceptions import ApplicationError


class ReportApi(object):
    """Service class for making requests to report-api"""

    @staticmethod
    def send_event(event_name, event_details):
        current_app.logger.info("Calling the report event endpoint of the Report API "
                                "with the following data: {}".format(event_details))
        payload = {"event_name": event_name,
                   "event_timestamp": datetime.now(timezone.utc).isoformat(),
                   "event_details": event_details}

        response = g.requests.post(
            "{}/v2.0/report_events".format(REPORT_API_BASE_URL),
            json=payload,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code != 201:
            current_app.logger.error("Failed to send event to report-api, status was {}".format(response.status_code))
            raise ApplicationError("Failed to send event to report-api, status was {}".format(response.status_code),
                                   "RP01")
