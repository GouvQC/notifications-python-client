import json
import uuid
from unittest.mock import patch, MagicMock, ANY

import pytest
from jsonschema import Draft4Validator

from integration_test.enums import EMAIL_TYPE, SMS_TYPE
from integration_test.generate_json import JSONBuilder
from integration_test.schemas.v2.notification_schemas import (
    get_notification_response,
    get_notifications_response,
    post_bulk_notifications_response,
    post_email_response,
    post_sms_response,
)
from integration_test.schemas.v2.template_schemas import (
    get_template_by_id_response,
    post_template_preview_response,
)
from integration_test.schemas.v2.templates_schemas import get_all_template_response
from notifications_python_client.notifications import NotificationsAPIClient

API_KEY = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

def check_headers(mock_session_instance):
    assert set(mock_session_instance.request.call_args[1]["headers"].keys()) == {'Content-type', 'Authorization',
                                                                                 'User-agent'}


def check_call_body(mock_session_instance, body: dict):
    assert json.loads(mock_session_instance.request.call_args[1]["data"]) == body


def check_call(mock_session_instance, verb, url):
    mock_session_instance.request.assert_called_once_with(verb, url, data=ANY,
                                                          headers=ANY, timeout=30)

def check_get_call(mock_session_instance, verb, url):
    mock_session_instance.request.assert_called_once_with(verb, url,
                                                          headers=ANY, timeout=30)

def check_get_call_with_params(mock_session_instance, verb, url):
    mock_session_instance.request.assert_called_once_with(verb, url,
                                                          headers=ANY, timeout=30, params=ANY)

@pytest.fixture
def mock_response():
    mock_response = MagicMock(name="response")
    return mock_response


@pytest.fixture
def mock_session_instance():
    request_session = MagicMock(name="actual_session")
    return request_session


@pytest.fixture
def notifications_client(mock_response, mock_session_instance):
    with patch(target = "requests.Session") as mock_session:

        mock_session.return_value = mock_session_instance
        mock_session_instance.request.return_value = mock_response
        val =  NotificationsAPIClient(
            base_url="base_url", api_key=API_KEY, client_id="client_id"
        )

        return val


def validate(json_to_validate, schema):
    validator = Draft4Validator(schema)
    validator.validate(json_to_validate, schema)


def test_send_sms_notification_test_response(notifications_client, mock_response, mock_session_instance):
    mobile_number = "+4382992998"
    template_id = "9090af3a-75b5-46d4-a7ce-0c1a174091fa"
    unique_name = str(uuid.uuid4())
    personalisation = {"name": unique_name}
    mock_response.json.return_value = JSONBuilder.from_schema(post_sms_response).merge_values(
        {"id": "7070bf3a-75b5-46d4-a7ce-0c1a174091fa", "content": {"body": unique_name}}).get_json_object()

    response = notifications_client.send_sms_notification(
        phone_number=mobile_number,
        template_id=template_id,
        personalisation=personalisation,
        sms_sender_id=None,
    )
    validate(response, post_sms_response)

    check_call(mock_session_instance, "POST", "base_url/v2/notifications/sms")

    check_call_body(mock_session_instance, {'personalisation': {'name': unique_name},
                                       'phone_number': '+4382992998',
                                       'template_id': template_id})

    check_headers(mock_session_instance)
    assert unique_name in response["content"]["body"]  # check placeholders are replaced
    assert response["id"] == "7070bf3a-75b5-46d4-a7ce-0c1a174091fa"


@pytest.mark.parametrize(
    ("table_header", "destination"),
    [
        ("email address", "user1@fun.com"),
        ("phone_number", "+4182232345")
    ])
def test_send_bulk_notifications_with_rows(notifications_client, mock_response, mock_session_instance, table_header, destination):
    """
    Teste l'envoi de notifications en masse via l'API.
    """

    template_id = "9090af3a-75b5-46d4-a7ce-0c1a174091fa"
    mock_response.json.return_value = (
        JSONBuilder.from_schema(post_bulk_notifications_response)
        .merge_values(
            {
                "data": {
                    "notification_count": 2,
                    "original_file_name": "Test Bulk Notification Integration",
                    "template": template_id}}).get_json_object()
    )


    rows = [
        [table_header, "name"],
        [destination, "Alice"],
        [destination, "Wok"]
    ]

    name = "Test Bulk Notification Integration"

    reference = "bulk_ref_integration_test"

    # Appel de la méthode send_bulk_notifications
    response = notifications_client.send_bulk_notifications(
        template_id=template_id,
        name=name,
        rows=rows,
        reference=reference,
    )

    # Validation de la réponse
    validate(response, post_bulk_notifications_response)
    check_call(mock_session_instance, "POST", "base_url/v2/notifications/bulk")
    check_call_body(mock_session_instance, {"template_id": template_id, "name": name, "rows": rows, "reference": reference})
    assert response["data"]["id"] is not None
    assert response["data"]["notification_count"] == 2
    assert response["data"]["original_file_name"] == name
    assert response["data"]["template"] == template_id

@pytest.mark.parametrize(
    ("header", "destination"),
    [
        ("email address", "user1@fun.com"),
        ("phone_number", "+4182232345")
    ])
def test_send_bulk_notifications_with_csv(notifications_client, mock_response, mock_session_instance, header, destination):
    """
    Teste l'envoi de notifications en masse avec un fichier CSV brut.
    """
    template_id = "9090af3a-75b5-46d4-a7ce-0c1a174091fa"
    mock_response.json.return_value = (
        JSONBuilder.from_schema(post_bulk_notifications_response)
        .merge_values(
            {
                "data": {
                    "notification_count": 2,
                    "original_file_name": "Bulk send email with personalisation",
                    "template": template_id}}).get_json_object()
    )

    csv_data = f"{header},name\n{destination},Alice\n{destination},Wok"
    name = "Bulk send email with personalisation"
    reference = "bulk_ref_integration_test_csv"

    # Appel de la méthode send_bulk_notifications
    response = notifications_client.send_bulk_notifications(
        template_id=template_id,
        name=name,
        csv=csv_data,
        reference=reference,
    )

    # Validation de la réponse
    check_call(mock_session_instance, "POST", "base_url/v2/notifications/bulk")
    check_call_body(mock_session_instance, {"template_id": template_id, "name": name, "csv": csv_data, "reference": reference})

    validate(response, post_bulk_notifications_response)
    assert response["data"]["id"] is not None
    assert response["data"]["notification_count"] == 2
    assert response["data"]["original_file_name"] == name
    assert response["data"]["template"] == template_id


def test_send_email_notification_test_response(notifications_client, mock_response, mock_session_instance):
    email_address = "chic@freakout.com"
    template_id = str(uuid.uuid4())
    unique_name = str(uuid.uuid4())
    personalisation = {"name": unique_name}

    mock_response.json.return_value = JSONBuilder.from_schema(post_email_response).merge_values({"id": "6060bf3a-75b5-46d4-a7ce-0c1a174091fa", "content": { "body": unique_name}}).get_json_object()

    response = notifications_client.send_email_notification(
        email_address=email_address,
        template_id=template_id,
        personalisation=personalisation,
        email_reply_to_id=None,
    )
    validate(response, post_email_response)
    check_call(mock_session_instance, "POST", "base_url/v2/notifications/email")
    check_call_body(mock_session_instance, {"email_address": email_address, "template_id": template_id, "personalisation": personalisation})
    assert unique_name in response["content"]["body"]  # check placeholders are replaced
    return response["id"]

@pytest.mark.parametrize(
    "notification_type",
    [
        EMAIL_TYPE, SMS_TYPE
    ])
def test_get_notification_by_id(notifications_client, mock_response, notification_type, mock_session_instance):

    uuid_notification_id = str(uuid.uuid4())
    mock_response.json.return_value = JSONBuilder.from_schema(get_notification_response).get_json_object()

    response = notifications_client.get_notification_by_id(uuid_notification_id)

    check_get_call(mock_session_instance, "GET", f"base_url/v2/notifications/{uuid_notification_id}")

    validate(response, get_notification_response)


def test_get_all_notifications(notifications_client, mock_response, mock_session_instance):
    single_notification_response = JSONBuilder.from_schema(get_notification_response).get_json_object()
    mock_response.json.return_value = JSONBuilder.from_schema(get_notifications_response).get_json_object()
    mock_response.json.return_value["notifications"] = [single_notification_response]

    response = notifications_client.get_all_notifications()
    check_get_call_with_params(mock_session_instance, "GET", "base_url/v2/notifications")
    validate(response, get_notifications_response)


@pytest.mark.parametrize(
    "notification_type",
    [
        EMAIL_TYPE, SMS_TYPE
    ])
def test_get_template_by_id(notifications_client, mock_response, notification_type, mock_session_instance):
    template_id = "8655dfa5-2771-43c1-82eb-6d5beb4535f2"

    mock_response.json.return_value = JSONBuilder.from_schema(get_template_by_id_response).merge_values({"id": template_id}).get_json_object()
    response = notifications_client.get_template(template_id)

    check_get_call(mock_session_instance, "GET", f"base_url/v2/template/{template_id}")
    validate(response, get_template_by_id_response)

    assert template_id == response["id"]

@pytest.mark.parametrize(
    ("notification_type", "subject"),
    [
        (EMAIL_TYPE, "Sujet"), (SMS_TYPE, None)
    ])
def test_get_template_by_id_and_version(notifications_client, mock_response, notification_type, subject,
                                        mock_session_instance):
    template_id = "7655dfa5-2771-43c1-82eb-6d5beb4535f4"
    mock_response.json.return_value = JSONBuilder.from_schema(get_template_by_id_response).merge_values({"id": template_id, "version": 1, "subject": subject}).get_json_object()

    response = notifications_client.get_template_version(template_id, 1)

    check_get_call(mock_session_instance, "GET", f"base_url/v2/template/{template_id}/version/1")
    validate(response, get_template_by_id_response)
    assert response["subject"] == subject
    assert template_id == response["id"]
    assert 1 == response["version"]


@pytest.mark.parametrize(
    ("notification_type", "subject"),
    [
        (EMAIL_TYPE, "Sujet"), (SMS_TYPE, None)
    ])
def test_post_template_preview(notifications_client, mock_response,  notification_type, subject):
    template_id = "6655dfa5-2771-43c1-82eb-6d5beb4535f9"
    unique_name = str(uuid.uuid4())
    personalisation = {"name": unique_name}

    mock_response.json.return_value = JSONBuilder.from_schema(post_template_preview_response).merge_values({"id": template_id, "version": 1, "subject": subject, "body": unique_name }).get_json_object()

    response = notifications_client.post_template_preview(template_id, personalisation)

    validate(response, post_template_preview_response)
    assert response["subject"] == subject
    assert template_id == response["id"]
    assert unique_name in response["body"]


def test_get_all_templates(notifications_client, mock_response, mock_session_instance):

    single_template_response = JSONBuilder.from_schema(get_template_by_id_response).get_json_object()
    mock_response.json.return_value = JSONBuilder.from_schema(get_all_template_response).get_json_object()
    mock_response.json.return_value["templates"] = [single_template_response]

    response = notifications_client.get_all_templates()
    check_get_call_with_params(mock_session_instance, "GET", "base_url/v2/templates")
    validate(response, get_all_template_response)

@pytest.mark.parametrize(
    "notification_type",
    [
        EMAIL_TYPE, SMS_TYPE
    ])
def test_get_all_templates_for_type(notifications_client, mock_response, notification_type, mock_session_instance):

    single_template_response = JSONBuilder.from_schema(get_template_by_id_response).get_json_object()
    mock_response.json.return_value = JSONBuilder.from_schema(get_all_template_response).get_json_object()
    mock_response.json.return_value["templates"] = [single_template_response]

    response = notifications_client.get_all_templates(notification_type)

    check_get_call_with_params(mock_session_instance, "GET", "base_url/v2/templates")
    validate(response, get_all_template_response)

def test_check_health_integration(notifications_client, mock_response):
    """
    Teste l'intégration de la méthode check_health avec l'API réelle.
    """
    mock_response.json.return_value = {"status": "ok"}
    response = notifications_client.check_health()

    assert response["status"] in ["ok", "unavailable"]
