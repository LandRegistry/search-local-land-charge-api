from flask import current_app, g
from search_local_land_charge_api.config import STORAGE_API
from search_local_land_charge_api.exceptions import ApplicationError


class StorageAPIService(object):

    @staticmethod
    def save_files(files, bucket, logger=None, requests=None):
        if not logger:
            logger = current_app.logger
        if not requests:
            requests = g.requests

        request_path = "{}/{}".format(STORAGE_API, bucket)

        logger.info("Calling storage api via this URL: %s", request_path)
        response = requests.post(request_path, files=files)
        if response.status_code == 201:
            return response.json()
        raise ApplicationError("Failed to store document", "ST01")
