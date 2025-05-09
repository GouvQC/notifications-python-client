# ruff: noqa: T201, T203
"""

Usage:
    make_api_call.py <base_url> <client-id> <secret> send-bulk --type=<type> --template-id=<id> \
        --name=<name> --reference=<ref> [--csv=<csv>] [--rows=<rows>]
    make_api_call.py <base_url> <client-id> <secret> create --type=<type> --template=<id> \
        --name=<name> --reference=<ref> [--to=<to>] [--personalisation=<json>] \
        [--sms_sender_id=<sender_id>]
    make_api_call.py <base_url> <client-id> <secret> fetch
    make_api_call.py <base_url> <client-id> <secret> fetch-all
    make_api_call.py <base_url> <client-id> <secret> fetch-generator
    make_api_call.py <base_url> <client-id> <secret> preview
    make_api_call.py <base_url> <client-id> <secret> template
    make_api_call.py <base_url> <client-id> <secret> all_templates
    make_api_call.py <base_url> <client-id> <secret> template_version
    make_api_call.py <base_url> <client-id> <secret> all_template_versions

Options:
    --type=<type>               Type of notification: email or sms.
    --to=<phone_number|email>   Target phone number or email for individual notification.
    --personalisation=<{}>      JSON object for dynamic data insertion in the notification.
    --sms_sender_id=<id>        SMS sender ID, if applicable.
    --template-id=<id>          ID of the template to use for the notification.
    --template=<id>             Alternative template ID (use either --template-id or --template).
    --name=<name>               Name of the bulk send.
    --reference=<ref>           Reference string for this bulk send.
    --csv=<csv>                 Raw CSV content for bulk send (optional, prompted if not provided).
    --rows=<rows>               Raw rows data in JSON format for bulk send (optional, prompted if not provided).

Example:
    ./make_api_call.py http://api my_service super_secret send-bulk --type=email --template-id=123 \
        --name="Bulk Email" --reference="ref001" --csv="email address,name\nuser@example.com,Alice"
    ./make_api_call.py http://api my_service super_secret send-bulk --type=sms  --template-id=456 \
       --name="Bulk SMS" --reference="ref002" --csv="phone number,name\n+1234567891,Bob\n+1234567891,Alice"
    ./make_api_call.py http://api my_service super_secret create --type=email --template=123 \
        --name="New Notification" --reference="ref003" --to="user@example.com"

"""

import json
import sys
from pprint import pprint

from docopt import docopt

from notifications_python_client.notifications import NotificationsAPIClient


def create_notification(notifications_client, **kwargs):
    notification_type = kwargs["--type"] or input("enter type email|sms: ")

    if notification_type == "sms":
        return create_sms_notification(notifications_client, **kwargs)
    if notification_type == "email":
        return create_email_notification(notifications_client, **kwargs)
    print(f"Invalid type: {notification_type}, exiting")
    sys.exit(1)


def create_sms_notification(notifications_client, **kwargs):
    mobile_number = kwargs["--to"] or input("enter number (+441234123123): ")
    template_id = kwargs["--template"] or input("template id: ")
    personalisation = kwargs["--personalisation"] or input("personalisation (JSON string):")
    personalisation = personalisation and json.loads(personalisation)
    reference = (
        kwargs["--reference"] if kwargs["--reference"] is not None else input("reference string for notification: ")
    )
    sms_sender_id = kwargs["--sms_sender_id"] or input("sms sender id: ")
    return notifications_client.send_sms_notification(
        mobile_number,
        template_id=template_id,
        personalisation=personalisation,
        reference=reference,
        sms_sender_id=sms_sender_id,
    )


def create_email_notification(notifications_client, **kwargs):
    email_address = kwargs["--to"] or input("enter email: ")
    template_id = kwargs["--template"] or input("template id: ")
    personalisation = kwargs["--personalisation"] or input("personalisation (as JSON):") or None
    personalisation = personalisation and json.loads(personalisation)
    reference = (
        kwargs["--reference"] if kwargs["--reference"] is not None else input("reference string for notification: ")
    )
    email_reply_to_id = input("email reply to id:")
    return notifications_client.send_email_notification(
        email_address,
        template_id=template_id,
        personalisation=personalisation,
        reference=reference,
        email_reply_to_id=email_reply_to_id,
    )


def get_notification(notifications_client):
    id = input("Notification id: ")
    return notifications_client.get_notification_by_id(id)


def get_all_notifications_generator(notifications_client):
    status = input("Notification status: ")
    template_type = input("Notification template type: ")
    reference = input("Notification reference: ")
    older_than = input("Older than notification id: ")
    generator = notifications_client.get_all_notifications_iterator(
        status=status, template_type=template_type, reference=reference, older_than=older_than
    )
    return generator


def get_all_notifications(notifications_client):
    status = input("Notification status: ")
    template_type = input("Notification template type: ")
    reference = input("Notification reference: ")
    older_than = input("Older than id: ")
    return notifications_client.get_all_notifications(
        status=status, template_type=template_type, reference=reference, older_than=older_than
    )


def preview_template(notifications_client):
    template_id = input("Template id: ")
    return notifications_client.get_template_preview(template_id)


def get_template(notifications_client):
    template_id = input("Template id: ")
    return notifications_client.get_template(template_id)


def get_all_templates(notifications_client):
    return notifications_client.get_all_templates()


def get_all_template_versions(notifications_client):
    template_id = input("Template id: ")
    return notifications_client.get_all_template_versions(template_id)


def get_template_version(notifications_client):
    template_id = input("Template id: ")
    version = input("Version: ")
    return notifications_client.get_template_version(template_id, version)


def send_bulk_notifications(notifications_client, **kwargs):
    # Récupérer le type de notification (email ou sms)
    notification_type = kwargs.get("--type") or input("Enter type: email | sms: ")
    template_id = kwargs.get("--template-id") or input("Enter template id: ")
    name = kwargs.get("--name") or input("Enter name: ")
    reference = kwargs.get("--reference") or input("Enter reference: ")

    # Initialiser la variable de données CSV ou Rows
    csv_data = kwargs.get("--csv")
    rows_data = kwargs.get("--rows")

    # Si le type est 'email'
    if notification_type == "email":
        if not csv_data:
            csv_data = input("Enter csv data for emails (e.g. 'email address,name\\nuser@example.com,Alice'): ")

        if not rows_data:
            rows_data = input(
                "Enter rows data for emails (e.g. [['email address', 'name'], ['user@example.com', 'Alice']]): "
            )

    # Si le type est 'sms'
    elif notification_type == "sms":
        if not csv_data:
            csv_data = input("Enter csv data for SMS (e.g. 'phone number,name\\n+11234567890,Alice'): ")

        if not rows_data:
            rows_data = input("Enter rows data for SMS (e.g. [['phone number', 'name'], ['+11234567890', 'Alice']]): ")

    else:
        print("Invalid notification type. Choose either 'email' or 'sms'.")
        sys.exit(1)

    # Si rows est fourni dans les arguments, essayer de le décoder
    if rows_data:
        try:
            rows = json.loads(rows_data)
        except json.JSONDecodeError:
            print("Invalid --rows value. Must be a valid JSON list of lists.")
            sys.exit(1)
        return notifications_client.send_bulk_notifications(
            template_id=template_id,
            name=name,
            rows=rows,
            reference=reference,
        )

    # Si csv_data est fourni mais pas rows, appeler avec csv_data
    if csv_data:
        return notifications_client.send_bulk_notifications(
            template_id=template_id,
            name=name,
            csv=csv_data,
            reference=reference,
        )

    print("Either --csv or --rows must be provided.")
    sys.exit(1)


def check_health(notifications_client):
    return notifications_client.check_health()


if __name__ == "__main__":
    arguments = docopt(__doc__)

    client = NotificationsAPIClient(
        base_url=arguments["<base_url>"], client_id=arguments["<client-id>"], api_key=arguments["<secret>"]
    )

    if arguments["<call>"] == "health":
        pprint(check_health(notifications_client=client))

    if arguments["<call>"] == "send-bulk":
        pprint(
            send_bulk_notifications(
                notifications_client=client, **{k: arguments[k] for k in arguments if k.startswith("--")}
            )
        )

    if arguments["<call>"] == "create":
        pprint(
            create_notification(
                notifications_client=client, **{k: arguments[k] for k in arguments if k.startswith("--")}
            )
        )

    if arguments["<call>"] == "fetch":
        pprint(get_notification(notifications_client=client))

    if arguments["<call>"] == "fetch-all":
        pprint(get_all_notifications(notifications_client=client))

    if arguments["<call>"] == "fetch-generator":
        pprint(list(get_all_notifications_generator(notifications_client=client)))

    if arguments["<call>"] == "preview":
        pprint(preview_template(notifications_client=client))

    if arguments["<call>"] == "template":
        pprint(get_template(notifications_client=client))

    if arguments["<call>"] == "all_templates":
        pprint(get_all_templates(notifications_client=client))

    if arguments["<call>"] == "template_version":
        pprint(get_template_version(notifications_client=client))

    if arguments["<call>"] == "all_template_versions":
        pprint(get_all_template_versions(notifications_client=client))
