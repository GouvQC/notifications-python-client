from tests.conftest import TEST_HOST


def test_get_notification_by_id(notifications_client, rmock):
    endpoint = f"{TEST_HOST}/v2/notifications/123"
    rmock.request("GET", endpoint, json={"status": "success"}, status_code=200)

    notifications_client.get_notification_by_id(123)

    assert rmock.called


def test_get_all_notifications_by_type_and_status(notifications_client, rmock):
    endpoint = f"{TEST_HOST}/v2/notifications?status=status&template_type=type"
    rmock.request("GET", endpoint, json={"status": "success"}, status_code=200)

    notifications_client.get_all_notifications("status", "type")

    assert rmock.called


def test_get_all_notifications_by_type(notifications_client, rmock):
    endpoint = f"{TEST_HOST}/v2/notifications?template_type=type"
    rmock.request("GET", endpoint, json={"status": "success"}, status_code=200)

    notifications_client.get_all_notifications(template_type="type")

    assert rmock.called


def test_get_all_notifications_by_reference(notifications_client, rmock):
    endpoint = f"{TEST_HOST}/v2/notifications?reference=reference"
    rmock.request("GET", endpoint, json={"status": "success"}, status_code=200)

    notifications_client.get_all_notifications(reference="reference")

    assert rmock.called


def test_get_all_notifications_by_older_than(notifications_client, rmock):
    endpoint = f"{TEST_HOST}/v2/notifications?older_than=older_than"
    rmock.request("GET", endpoint, json={"status": "success"}, status_code=200)

    notifications_client.get_all_notifications(older_than="older_than")

    assert rmock.called


def test_get_all_notifications_by_status(notifications_client, rmock):
    endpoint = f"{TEST_HOST}/v2/notifications?status=status"
    rmock.request("GET", endpoint, json={"status": "success"}, status_code=200)

    notifications_client.get_all_notifications(status="status")

    assert rmock.called


def test_get_all_notifications(notifications_client, rmock):
    endpoint = f"{TEST_HOST}/v2/notifications"
    rmock.request("GET", endpoint, json={"status": "success"}, status_code=200)

    notifications_client.get_all_notifications()

    assert rmock.called


def test_create_sms_notification(notifications_client, rmock):
    endpoint = f"{TEST_HOST}/v2/notifications/sms"
    rmock.request("POST", endpoint, json={"status": "success"}, status_code=200)

    notifications_client.send_sms_notification(phone_number="07700 900000", template_id="456")

    assert rmock.last_request.json() == {"template_id": "456", "phone_number": "07700 900000"}


def test_create_sms_notification_with_personalisation(notifications_client, rmock):
    endpoint = f"{TEST_HOST}/v2/notifications/sms"
    rmock.request("POST", endpoint, json={"status": "success"}, status_code=200)

    notifications_client.send_sms_notification(
        phone_number="07700 900000", template_id="456", personalisation={"name": "chris"}
    )

    assert rmock.last_request.json() == {
        "template_id": "456",
        "phone_number": "07700 900000",
        "personalisation": {"name": "chris"},
    }


def test_create_sms_notification_with_sms_sender_id(notifications_client, rmock):
    endpoint = f"{TEST_HOST}/v2/notifications/sms"
    rmock.request("POST", endpoint, json={"status": "success"}, status_code=200)

    notifications_client.send_sms_notification(phone_number="07700 900000", template_id="456", sms_sender_id="789")

    assert rmock.last_request.json() == {"template_id": "456", "phone_number": "07700 900000", "sms_sender_id": "789"}


def test_create_email_notification(notifications_client, rmock):
    endpoint = f"{TEST_HOST}/v2/notifications/email"
    rmock.request("POST", endpoint, json={"status": "success"}, status_code=200)

    notifications_client.send_email_notification(email_address="to@example.com", template_id="456")

    assert rmock.last_request.json() == {"template_id": "456", "email_address": "to@example.com"}


def test_create_email_notification_with_email_reply_to_id(notifications_client, rmock):
    endpoint = f"{TEST_HOST}/v2/notifications/email"
    rmock.request("POST", endpoint, json={"status": "success"}, status_code=200)

    notifications_client.send_email_notification(
        email_address="to@example.com", template_id="456", email_reply_to_id="789"
    )

    assert rmock.last_request.json() == {
        "template_id": "456",
        "email_address": "to@example.com",
        "email_reply_to_id": "789",
    }


def test_create_email_notification_with_personalisation(notifications_client, rmock):
    endpoint = f"{TEST_HOST}/v2/notifications/email"
    rmock.request("POST", endpoint, json={"status": "success"}, status_code=200)

    notifications_client.send_email_notification(
        email_address="to@example.com", template_id="456", personalisation={"name": "chris"}
    )

    assert rmock.last_request.json() == {
        "template_id": "456",
        "email_address": "to@example.com",
        "personalisation": {"name": "chris"},
    }


def test_get_all_notifications_iterator_calls_get_notifications(notifications_client, rmock):
    endpoint = f"{TEST_HOST}/v2/notifications"
    rmock.request("GET", endpoint, json={"status": "success"}, status_code=200)

    list(notifications_client.get_all_notifications_iterator())

    assert rmock.called


def test_get_all_notifications_iterator_stops_if_empty_notification_list_returned(notifications_client, rmock):
    responses = [
        _generate_response("79f9c6ce-cd6a-4b47-a3e7-41e155f112b0", [1, 2]),
        _generate_response("3e8f2f0a-0f2b-4d1b-8a01-761f14a281bb", []),
    ]

    endpoint = f"{TEST_HOST}/v2/notifications"
    rmock.request("GET", endpoint, responses)

    list(notifications_client.get_all_notifications_iterator())
    assert rmock.call_count == 2


def test_get_all_notifications_iterator_gets_more_notifications_with_correct_id(notifications_client, rmock):
    responses = [
        _generate_response("79f9c6ce-cd6a-4b47-a3e7-41e155f112b0", [1, 2]),
        _generate_response("ea179232-3190-410d-b8ab-23dfecdd3157", [3, 4]),
        _generate_response("3e8f2f0a-0f2b-4d1b-8a01-761f14a281bb", []),
    ]

    endpoint = f"{TEST_HOST}/v2/notifications"
    rmock.request("GET", endpoint, responses)
    list(notifications_client.get_all_notifications_iterator())
    assert rmock.call_count == 3


def test_get_template(notifications_client, rmock):
    endpoint = f"{TEST_HOST}/v2/template/{123}"
    rmock.request("GET", endpoint, json={"status": "success"}, status_code=200)

    notifications_client.get_template(123)

    assert rmock.called


def test_get_template_version(notifications_client, rmock):
    endpoint = f"{TEST_HOST}/v2/template/123/version/1"
    rmock.request("GET", endpoint, json={"status": "success"}, status_code=200)

    notifications_client.get_template_version(123, 1)

    assert rmock.called


def test_post_template_preview(notifications_client, rmock):
    endpoint = f"{TEST_HOST}/v2/template/123/preview"
    rmock.request("POST", endpoint, json={"status": "success"}, status_code=200)

    notifications_client.post_template_preview(123, personalisation={"name": "chris"})

    assert rmock.called
    assert rmock.last_request.json() == {"personalisation": {"name": "chris"}}


def test_get_all_templates(notifications_client, rmock):
    endpoint = f"{TEST_HOST}/v2/templates"
    rmock.request("GET", endpoint, json={"status": "success"}, status_code=200)

    notifications_client.get_all_templates()

    assert rmock.called


def test_get_all_templates_by_type(notifications_client, rmock):
    endpoint = f"{TEST_HOST}/v2/templates?type=type"
    rmock.request("GET", endpoint, json={"status": "success"}, status_code=200)

    notifications_client.get_all_templates("type")

    assert rmock.called


def _generate_response(next_link_uuid, notifications: list):
    return {
        "json": {
            "notifications": notifications,
            "links": {"next": f"http://localhost:6011/v2/notifications?older_than={next_link_uuid}"},
        },
        "status_code": 200,
    }
