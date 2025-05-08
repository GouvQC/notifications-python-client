import os
import time
import uuid

from jsonschema import Draft4Validator

from integration_test.enums import EMAIL_TYPE, SMS_TYPE
from integration_test.schemas.v2.notification_schemas import (
    get_notification_response,
    get_notifications_response,
    post_email_response,
    post_sms_response,
    post_bulk_notifications_response,
)
from integration_test.schemas.v2.template_schemas import (
    get_template_by_id_response,
    post_template_preview_response,
)
from integration_test.schemas.v2.templates_schemas import get_all_template_response
from notifications_python_client.notifications import NotificationsAPIClient


def validate(json_to_validate, schema):
    validator = Draft4Validator(schema)
    validator.validate(json_to_validate, schema)


def send_sms_notification_test_response(python_client, sender_id=None):
    mobile_number = os.environ["FUNCTIONAL_TEST_NUMBER"]
    template_id = os.environ["SMS_TEMPLATE_ID"]
    unique_name = str(uuid.uuid4())
    personalisation = {"name": unique_name}
    sms_sender_id = sender_id
    response = python_client.send_sms_notification(
        phone_number=mobile_number,
        template_id=template_id,
        personalisation=personalisation,
        sms_sender_id=sms_sender_id,
    )
    validate(response, post_sms_response)
    assert unique_name in response["content"]["body"]  # check placeholders are replaced
    return response["id"]


def send_bulk_notifications_with_rows(notifications_client, notification_type):
    """
    Teste l'envoi de notifications en masse via l'API.
    """

    functional_test_email = os.environ["FUNCTIONAL_TEST_EMAIL"]
    functional_phone_number = os.environ["FUNCTIONAL_TEST_NUMBER"]

    if notification_type == EMAIL_TYPE:
        template_id = os.environ["EMAIL_TEMPLATE_ID"]
        rows = [
            ["email address", "name"],
            [functional_test_email, "Alice"],
            [functional_test_email, "Wok"],
        ]
    elif notification_type == SMS_TYPE:
        template_id = os.environ["SMS_TEMPLATE_ID"]
        rows = [
            ["phone number", "name"],
            [functional_phone_number, "Alice"],
            [functional_phone_number, "Wok"],
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
    assert response["data"]["id"] is not None
    assert response["data"]["notification_count"] == 2
    assert response["data"]["original_file_name"] == name
    assert response["data"]["template"] == template_id


def send_bulk_notifications_with_csv(notifications_client, notification_type):
    """
    Teste l'envoi de notifications en masse avec un fichier CSV brut.
    """
    functional_test_email = os.environ["FUNCTIONAL_TEST_EMAIL"]
    functional_phone_number = os.environ["FUNCTIONAL_TEST_NUMBER"]

    if notification_type == EMAIL_TYPE:
        template_id = os.environ["EMAIL_TEMPLATE_ID"]
        csv_data = f"email address,name\n{functional_test_email},Alice\n{functional_test_email},Wok"
    elif notification_type == SMS_TYPE:
        template_id = os.environ["SMS_TEMPLATE_ID"]
        csv_data = f"phone number,name\n{functional_phone_number},Alice\n{functional_phone_number},Wok"

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
    validate(response, post_bulk_notifications_response)
    assert response["data"]["id"] is not None
    assert response["data"]["notification_count"] == 2
    assert response["data"]["original_file_name"] == name
    assert response["data"]["template"] == template_id


def send_email_notification_test_response(python_client, reply_to=None):
    email_address = os.environ["FUNCTIONAL_TEST_EMAIL"]
    template_id = os.environ["EMAIL_TEMPLATE_ID"]
    email_reply_to_id = reply_to
    unique_name = str(uuid.uuid4())
    personalisation = {"name": unique_name}
    response = python_client.send_email_notification(
        email_address=email_address,
        template_id=template_id,
        personalisation=personalisation,
        email_reply_to_id=email_reply_to_id,
    )
    validate(response, post_email_response)
    assert unique_name in response["content"]["body"]  # check placeholders are replaced
    return response["id"]


def get_notification_by_id(python_client, id, notification_type):
    response = python_client.get_notification_by_id(id)
    if notification_type == EMAIL_TYPE:
        validate(response, get_notification_response)
    elif notification_type == SMS_TYPE:
        validate(response, get_notification_response)
    else:
        raise KeyError("notification type should be email|sms")


def get_all_notifications(client):
    response = client.get_all_notifications()
    validate(response, get_notifications_response)


def get_template_by_id(python_client, template_id, notification_type):
    response = python_client.get_template(template_id)

    if notification_type == EMAIL_TYPE:
        validate(response, get_template_by_id_response)
    elif notification_type == SMS_TYPE:
        validate(response, get_template_by_id_response)
        assert response["subject"] is None
    else:
        raise KeyError("template type should be email|sms")

    assert template_id == response["id"]


def get_template_by_id_and_version(python_client, template_id, version, notification_type):
    response = python_client.get_template_version(template_id, version)

    if notification_type == EMAIL_TYPE:
        validate(response, get_template_by_id_response)
    elif notification_type == SMS_TYPE:
        validate(response, get_template_by_id_response)
        assert response["subject"] is None
    else:
        raise KeyError("template type should be email|sms")

    assert template_id == response["id"]
    assert version == response["version"]


def post_template_preview(python_client, template_id, notification_type):
    unique_name = str(uuid.uuid4())
    personalisation = {"name": unique_name}

    response = python_client.post_template_preview(template_id, personalisation)

    if notification_type == EMAIL_TYPE:
        validate(response, post_template_preview_response)
    elif notification_type == SMS_TYPE:
        validate(response, post_template_preview_response)
        assert response["subject"] is None
    else:
        raise KeyError("template type should be email|sms")

    assert template_id == response["id"]
    assert unique_name in response["body"]


def get_all_templates(python_client):
    response = python_client.get_all_templates()
    validate(response, get_all_template_response)


def get_all_templates_for_type(python_client, template_type):
    response = python_client.get_all_templates(template_type)
    validate(response, get_all_template_response)


def retry_get_notification_by_id(python_client, id, notification_type, max_retries=5, delay=3):
    from requests.exceptions import HTTPError

    for _attempt in range(max_retries):
        try:
            response = python_client.get_notification_by_id(id)
            if notification_type == EMAIL_TYPE or notification_type == SMS_TYPE:
                validate(response, get_notification_response)
                return
            else:
                raise KeyError("notification type should be email|sms")
        except HTTPError as e:
            if e.response.status_code == 404:
                time.sleep(delay)
            else:
                raise
    raise RuntimeError(f"Notification {id} not found after {max_retries} retries")


def check_health_integration(notifications_client):
    """
    Teste l'intégration de la méthode check_health avec l'API réelle.
    """
    response = notifications_client.check_health()

    assert response["status"] in ["ok", "unavailable"]


def test_integration():
    client = NotificationsAPIClient(
        base_url=os.environ["NOTIFY_API_URL"], api_key=os.environ["API_KEY"], client_id=os.environ["CLIENT_ID"]
    )
    # client_using_team_key = NotificationsAPIClient(
    #     base_url=os.environ["NOTIFY_API_URL"],
    #     api_key=os.environ["API_SENDING_KEY"],
    #     client_id=os.environ["CLIENT_ID"]
    # )

    sms_template_id = os.environ["SMS_TEMPLATE_ID"]
    sms_sender_id = os.environ["SMS_SENDER_ID"]
    email_template_id = os.environ["EMAIL_TEMPLATE_ID"]
    email_reply_to_id = os.environ["EMAIL_REPLY_TO_ID"]

    assert sms_template_id
    assert sms_sender_id
    assert email_template_id
    assert email_reply_to_id

    version_number = 1

    check_health_integration(client)

    send_bulk_notifications_with_csv(client, SMS_TYPE)
    send_bulk_notifications_with_csv(client, EMAIL_TYPE)

    send_bulk_notifications_with_rows(client, SMS_TYPE)
    send_bulk_notifications_with_rows(client, EMAIL_TYPE)


    # get_template_by_id(client, sms_template_id, SMS_TYPE)
    # get_template_by_id(client, email_template_id, EMAIL_TYPE)
    # get_template_by_id_and_version(client, sms_template_id, version_number, SMS_TYPE)
    # get_template_by_id_and_version(client, email_template_id, version_number, EMAIL_TYPE)
    # post_template_preview(client, sms_template_id, SMS_TYPE)
    # post_template_preview(client, email_template_id, EMAIL_TYPE)
    # get_all_templates(client)
    # get_all_templates_for_type(client, EMAIL_TYPE)
    # get_all_templates_for_type(client, SMS_TYPE)



    # sms_id = send_sms_notification_test_response(client)

    # email_id = send_email_notification_test_response(client)
    # # # print("SMS ID envoyé par le test:", sms_id)
    # # # print("EMAIL ID envoyé par le test:", email_id)

    # get_all_notifications(client)

    # time.sleep(5)
    # get_notification_by_id(client, email_id, EMAIL_TYPE)
    # get_notification_by_id(client, sms_id, SMS_TYPE)

    # # retry_get_notification_by_id(client, sms_id, SMS_TYPE)
    # # retry_get_notification_by_id(client, email_id, EMAIL_TYPE)

    # # sms_with_sender_id = send_sms_notification_test_response(client_using_team_key, sms_sender_id)
    # # email_with_reply_id = send_email_notification_test_response(client, email_reply_to_id)

    # # get_notification_by_id(client, sms_with_sender_id, SMS_TYPE)
    # # get_notification_by_id(client, email_with_reply_id, EMAIL_TYPE)

    print("notifications-python-client integration tests are successful")  # noqa: T201


if __name__ == "__main__":
    test_integration()
