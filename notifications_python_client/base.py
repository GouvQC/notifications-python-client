import json
import logging
import time

import requests

from notifications_python_client import __version__
from notifications_python_client.authentication import create_jwt_token
from notifications_python_client.errors import HTTPError, InvalidResponse

logger = logging.getLogger(__name__)


class BaseAPIClient:
    """
    Base class for PGN API client.

     Args:
        api_key (str): The combined API key used to authenticate requests to the Notification API.
        client_id (str or None): Optional. Required only if the proxy is MCN (PGGAPI).
    """

    def __init__(self, api_key, client_id=None, base_url="https://gw-gouvqc.mcn.api.gouv.qc.ca/pgn", timeout=30):
        """
        Initialise the client
        Error if either of base_url or secret missing
        :param base_url - base URL of PGN API:
        :param secret - application secret - used to sign the request:
        :param timeout - request timeout on the client
        :return:
        """
        service_id = api_key[-73:-37]
        api_key = api_key[-36:]

        if not base_url:
            raise ValueError("Missing base url")
        if not service_id:
            raise ValueError("Missing service ID")
        if not api_key:
            raise ValueError("Missing API key")

        if "mcn.api.gouv.qc.ca" in base_url and not client_id:
            raise ValueError("A valid client identifier (X-QC-Client-Id) is required when using the PGGAPI proxy.")

        self.client_id = client_id
        self.base_url = base_url
        self.service_id = service_id
        self.api_key = api_key
        self.timeout = timeout
        self.request_session = requests.Session()

    def put(self, url, data):
        return self.request("PUT", url, data=data)

    def get(self, url, params=None):
        """Send a GET request."""
        return self.request("GET", url, params=params)

    def post(self, url, data):
        """Send a POST request."""
        return self.request("POST", url, data=data)

    def delete(self, url, data=None):
        """Send a DELETE request."""
        return self.request("DELETE", url, data=data)

    def generate_headers(self, api_token, url):
        """
        Generates headers including the Bearer Token
        and the mandatory X-QC-Client-Id for the PGGAPI.
        """
        headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {api_token}",
            "User-agent": f"NOTIFY-API-PYTHON-CLIENT/{__version__}",
        }

        if "mcn.api.gouv.qc.ca" in url and self.client_id:
            headers["X-QC-Client-Id"] = self.client_id

        return headers

    def request(self, method, url, data=None, params=None):
        logger.debug("API request %s %s", method, url)
        url, kwargs = self._create_request_objects(url, data, params)

        response = self._perform_request(method, url, kwargs)

        return self._process_json_response(response)

    def _create_request_objects(self, url, data, params):
        # Construire l'URL complète sans supprimer le chemin de base
        if not self.base_url.endswith("/"):
            self.base_url += "/"
        url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"

        api_token = create_jwt_token(self.api_key, self.service_id)

        kwargs = {"headers": self.generate_headers(api_token, url), "timeout": self.timeout}

        if data is not None:
            kwargs.update(data=self._serialize_data(data))

        if params is not None:
            kwargs.update(params=params)

        return url, kwargs

    def _serialize_data(self, data):
        return json.dumps(data, default=self._extended_json_encoder)

    def _extended_json_encoder(self, obj):
        if isinstance(obj, set):
            return list(obj)

        raise TypeError

    def _perform_request(self, method, url, kwargs):
        start_time = time.monotonic()
        try:
            response = self.request_session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            api_error = HTTPError.create(e)
            logger.warning(
                "API %s request on %s failed with %s '%s'", method, url, api_error.status_code, api_error.message
            )
            raise api_error from e
        finally:
            elapsed_time = time.monotonic() - start_time
            logger.debug("API %s request on %s finished in %s", method, url, elapsed_time)

    def _process_json_response(self, response):
        try:
            if response.status_code == 204:
                return
            return response.json()
        except ValueError as e:
            raise InvalidResponse(response, message="No JSON response object could be decoded") from e
