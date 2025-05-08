import pytest

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


@pytest.mark.parametrize(
    "rows, csv, expected_error",
    [
        # Cas où `rows` est fourni
        (
            [["email address", "name"], ["Alice@exemple.ca", "Alice"], ["Wok@exemple.ca", "Wok"]],
            None,
            None,
        ),
        # Cas où `csv` est fourni
        (
            None,
            "phone number,name\n5142346159,Alice\n5140001122,Wok",
            None,
        ),
        # Cas où ni `rows` ni `csv` ne sont fournis
        (None, None, ValueError),
        # Cas où les deux `rows` et `csv` sont fournis
        (
            [["phone number", "name"], ["n5142346159", "Alice"], ["n5140001122", "Wok"]],
            "phone number,name\n5142346159,Alice\n5140001122,Wok",
            ValueError,
        ),
    ],
)
def test_send_bulk_notifications_validation(rows, csv, expected_error, notifications_client, rmock):
    """
    Teste la validation des paramètres `rows` et `csv` pour la méthode send_bulk_notifications.
    """
    endpoint = f"{TEST_HOST}/v2/notifications/bulk"
    template_id = "template-id-123"
    name = "Test Bulk Notification"
    reference = "bulk_ref_test"

    if expected_error:
        # Vérifie que l'exception attendue est levée
        with pytest.raises(expected_error):
            notifications_client.send_bulk_notifications(
                template_id=template_id,
                name=name,
                rows=rows,
                csv=csv,
                reference=reference,
            )
    else:
        # Mock de la réponse de l'API
        rmock.request(
            "POST",
            endpoint,
            json={
                "data": {
                    "id": "bulk-notification-id",
                    "job_status": "pending",
                    "notification_count": 2,
                    "original_file_name": name,
                    "template": template_id,
                    "template_version": 1,
                }
            },
            status_code=201,
        )

        # Appel de la méthode avec des paramètres valides
        response = notifications_client.send_bulk_notifications(
            template_id=template_id,
            name=name,
            rows=rows,
            csv=csv,
            reference=reference,
        )

        # Vérifie que le mock a été appelé
        assert rmock.called
        assert rmock.last_request.json() == {
            "template_id": template_id,
            "name": name,
            **({"rows": rows} if rows else {}),
            **({"csv": csv} if csv else {}),
            "reference": reference,
        }

        # Vérifie que la réponse contient les données simulées
        assert response["data"]["id"] == "bulk-notification-id"
        assert response["data"]["job_status"] == "pending"
        assert response["data"]["notification_count"] == 2
        assert response["data"]["original_file_name"] == name
        assert response["data"]["template"] == template_id
        assert response["data"]["template_version"] == 1


def test_send_bulk_notifications_with_rows(rmock, notifications_client):
    """
    Teste l'envoi de notifications email en masse avec des lignes de données (rows).
    """
    endpoint = f"{TEST_HOST}/v2/notifications/bulk"
    template_id = "template-id-123"
    name = "Bulk send email with personalisation"
    rows = [
        ["email address", "name"],
        ["radouane.boutiri-ext@mcn.gouv.qc.ca", "Alice"],
        ["radouane.boutiri-ext@mcn.gouv.qc.ca", "Wok"]
    ]
    reference = "bulk_ref_test_rows"

    # Mock de la réponse de l'API
    rmock.request(
        "POST",
        endpoint,
        json={
            "data": {
                "id": "bulk-notification-id",
                "job_status": "pending",
                "notification_count": 2,
                "original_file_name": name,
                "template": template_id,
                "template_version": 1,
            }
        },
        status_code=201,
    )

    response = notifications_client.send_bulk_notifications(
        template_id=template_id,
        name=name,
        rows=rows,
        reference=reference,
    )

    assert rmock.called
    assert response["data"]["id"] == "bulk-notification-id"
    assert response["data"]["job_status"] == "pending"
    assert response["data"]["notification_count"] == 2
    assert response["data"]["original_file_name"] == name
    assert response["data"]["template"] == template_id
    assert response["data"]["template_version"] == 1


def test_send_bulk_notifications_with_csv(rmock, notifications_client):
    """
    Teste l'envoi de notifications sms en masse avec un fichier CSV brut.
    """
    endpoint = f"{TEST_HOST}/v2/notifications/bulk"
    template_id = "template-id-123"
    name = "Bulk send sms with personalisation"
    csv_data = "phone number,name\n5144442233,Alice\5142231234,Wok"
    reference = "bulk_ref_test_csv"

    # Mock de la réponse de l'API
    rmock.request(
        "POST",
        endpoint,
        json={
            "data": {
                "id": "bulk-notification-id",
                "job_status": "pending",
                "notification_count": 2,
                "original_file_name": name,
                "template": template_id,
                "template_version": 1,
            }
        },
        status_code=201,
    )

    response = notifications_client.send_bulk_notifications(
        template_id=template_id,
        name=name,
        csv=csv_data,
        reference=reference,
    )

    assert rmock.called
    assert response["data"]["id"] == "bulk-notification-id"
    assert response["data"]["job_status"] == "pending"
    assert response["data"]["notification_count"] == 2
    assert response["data"]["original_file_name"] == name
    assert response["data"]["template"] == template_id
    assert response["data"]["template_version"] == 1


def test_check_health(notifications_client, rmock):
    """
    Teste la méthode check_health pour vérifier l'état de santé du service.
    """
    endpoint = f"{TEST_HOST}/health"
    rmock.request("GET", endpoint, json={"status": "ok"}, status_code=200)

    response = notifications_client.check_health()

    assert rmock.called
    assert response["status"] == "ok"


def _generate_response(next_link_uuid, notifications: list):
    return {
        "json": {
            "notifications": notifications,
            "links": {"next": f"http://localhost:6011/v2/notifications?older_than={next_link_uuid}"},
        },
        "status_code": 200,
    }
