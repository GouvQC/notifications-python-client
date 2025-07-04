import re
from unittest import mock

import pytest
import requests

from notifications_python_client.base import BaseAPIClient
from notifications_python_client.errors import HTTPError, InvalidResponse
from tests.conftest import API_KEY_ID, CLIENT_ID, COMBINED_API_KEY, SERVICE_ID


@pytest.mark.parametrize(
    "client",
    [
        BaseAPIClient(api_key=COMBINED_API_KEY, client_id=CLIENT_ID),
        BaseAPIClient(COMBINED_API_KEY, CLIENT_ID),
    ],
    ids=["combined api key", "positional api key"],
)
def test_passes_through_service_id_and_key(rmock, client):
    with mock.patch("notifications_python_client.base.create_jwt_token") as mock_create_token:
        rmock.request("GET", "https://gw-gouvqc.mcn.api.gouv.qc.ca/pgn/", status_code=204)
        client.request("GET", "/")
    mock_create_token.assert_called_once_with(API_KEY_ID, SERVICE_ID)
    assert client.base_url == "https://gw-gouvqc.mcn.api.gouv.qc.ca/pgn/"


def test_can_set_base_url():
    client = BaseAPIClient(base_url="https://example.com/api", api_key=COMBINED_API_KEY, client_id=CLIENT_ID)
    assert client.base_url == "https://example.com/api"


def test_set_timeout():
    client = BaseAPIClient(base_url="foo", api_key=COMBINED_API_KEY, timeout=2, client_id=CLIENT_ID)
    assert client.timeout == 2


def test_default_timeout_is_set(base_client):
    assert base_client.timeout == 30


def test_allows_client_id_missing_if_not_mcn_url():
    client = BaseAPIClient(api_key=COMBINED_API_KEY, base_url="https://api.example.com")
    assert client.client_id is None


def test_fails_if_client_id_missing_and_url_is_mcn():
    with pytest.raises(ValueError) as err:
        BaseAPIClient(api_key=COMBINED_API_KEY, base_url="https://gw-gouvqc.mcn.api.gouv.qc.ca/pgn")
    assert str(err.value) == "A valid client identifier (X-QC-Client-Id) is required when using the PGGAPI proxy."


def test_fails_if_service_id_missing():
    with pytest.raises(ValueError) as err:
        BaseAPIClient(api_key=API_KEY_ID, client_id=CLIENT_ID)
    assert str(err.value) == "Missing service ID"


def test_connection_error_raises_api_error(base_client, rmock_patch):
    rmock_patch.side_effect = requests.exceptions.ConnectionError(None)

    with pytest.raises(HTTPError) as e:
        base_client.request("GET", "/")

    assert str(e.value) == "503 - Request failed"
    assert e.value.message == "Request failed"
    assert e.value.status_code == 503


def test_http_error_raises_api_error(base_client, rmock):
    rmock.request("GET", "http://test-host/", text="Internal Error", status_code=500)

    with pytest.raises(HTTPError) as e:
        base_client.request("GET", "/")

    assert str(e.value) == "500 - Request failed"
    assert e.value.message == "Request failed"
    assert e.value.status_code == 500


def test_non_2xx_response_raises_api_error(base_client, rmock):
    rmock.request("GET", "http://test-host/", json={"errors": "Not found"}, status_code=404)

    with pytest.raises(HTTPError) as e:
        base_client.request("GET", "/")

    assert str(e.value) == "404 - Not found"
    assert e.value.message == "Not found"
    assert e.value.status_code == 404


def test_invalid_json_raises_api_error(base_client, rmock):
    rmock.request("GET", "http://test-host/", text="Internal Error", status_code=200)

    with pytest.raises(InvalidResponse) as e:
        base_client.request("GET", "/")

    assert str(e.value) == "200 - No JSON response object could be decoded"
    assert e.value.message == "No JSON response object could be decoded"
    assert e.value.status_code == 200


def test_get_is_not_sent_with_body(base_client, rmock):
    rmock.request("GET", "http://test-host/", json={}, status_code=200)

    base_client.request("GET", "/")
    assert rmock.last_request.body is None


def test_user_agent_is_set(base_client, rmock):
    rmock.request("GET", "http://test-host/", json={}, status_code=200)

    base_client.request("GET", "/")

    assert re.fullmatch(
        r"NOTIFY-API-PYTHON-CLIENT\/(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(\+.*)",
        rmock.last_request.headers.get("User-Agent"),
    )


@pytest.mark.parametrize("data, expected_json", [[{"list": {1, 2}}, {"list": [1, 2]}]])
def test_converts_extended_types_to_json(base_client, rmock, data, expected_json):
    rmock.request(
        "GET",
        "http://test-host/",
        json=expected_json,
    )

    base_client.request("GET", "/", data=data)


def test_client_id_is_added_to_headers(base_client, rmock):
    # Définir la base_url correctement
    base_client.base_url = "https://gw-gouvqc.mcn.api.gouv.qc.ca/pgn"

    # Mock pour l'URL complète
    rmock.request("GET", "https://gw-gouvqc.mcn.api.gouv.qc.ca/pgn/resource", json={}, status_code=200)

    # Définir le client_id
    base_client.client_id = "test-client-id"

    # Effectuer la requête
    base_client.request("GET", "resource")

    # Vérification que le client_id est ajouté aux en-têtes
    assert rmock.last_request.headers.get("X-QC-Client-Id") == "test-client-id"


def test_client_id_header_absent_if_not_set(base_client, rmock):
    rmock.request("GET", "http://test-host/", json={}, status_code=200)

    base_client.client_id = None
    base_client.request("GET", "/")

    assert "X-QC-Client-Id" not in rmock.last_request.headers
