# ruff: noqa: T201, T203
"""

Usage:
  make_api_call.py <base_url> <client-id> <secret> health
  make_api_call.py <base_url> <client-id> <secret> fetch
  make_api_call.py <base_url> <client-id> <secret> fetch-all
  make_api_call.py <base_url> <client-id> <secret> fetch-generator
  make_api_call.py <base_url> <client-id> <secret> preview
  make_api_call.py <base_url> <client-id> <secret> template
  make_api_call.py <base_url> <client-id> <secret> all_templates
  make_api_call.py <base_url> <client-id> <secret> template_version
  make_api_call.py <base_url> <client-id> <secret> all_template_versions
  make_api_call.py <base_url> <client-id> <secret> send-bulk
  make_api_call.py <base_url> <client-id> <secret> create


"""

import json
import sys
from pprint import pprint

from docopt import docopt

from notifications_python_client.notifications import NotificationsAPIClient


def create_notification(notifications_client, **kwargs):
    notification_type = kwargs.get("--type") or input("Enter type: email | sms: ")
    if notification_type == "sms":
        return create_sms_notification(notifications_client, **kwargs)
    if notification_type == "email":
        return create_email_notification(notifications_client, **kwargs)
    print(f"Invalid type: {notification_type}, exiting")
    sys.exit(1)


def create_sms_notification(notifications_client, **kwargs):
    mobile_number = kwargs.get("--to") or input("enter number (+441234123123): ")
    template_id = kwargs.get("--template") or input("template id: ")
    personalisation = kwargs.get("--personalisation") or input("personalisation (JSON string) or press enter to skip: ")
    personalisation = personalisation and json.loads(personalisation)
    reference = (
        kwargs.get("--reference")
        if kwargs.get("--reference") is not None
        else input("reference string for notification or press enter to skip:: ")
    )
    sms_sender_id = kwargs.get("--sms_sender_id") or input("sms sender id or press enter to skip: ")
    return notifications_client.send_sms_notification(
        mobile_number,
        template_id=template_id,
        personalisation=personalisation,
        reference=reference,
        sms_sender_id=sms_sender_id,
    )


def create_email_notification(notifications_client, **kwargs):
    # Required fields
    email_address = kwargs.get("--to") or input("enter email: ")
    template_id = kwargs.get("--template") or input("template id: ")

    # Optional fields with cleanup
    personalisation_input = kwargs.get("--personalisation") or input(
        "personalisation (as JSON) or press enter to skip: "
    )
    personalisation = json.loads(personalisation_input) if personalisation_input else None

    reference_input = (
        kwargs.get("--reference")
        if kwargs.get("--reference") is not None
        else input("reference string for notification or press enter to skip: ")
    )
    reference = reference_input if reference_input else None

    email_reply_to_id_input = input("email reply to id or press enter to skip: ")
    email_reply_to_id = email_reply_to_id_input if email_reply_to_id_input else None

    scheduled_for_input = input("scheduled for (YYYY-MM-DDThh:mm:ss.000Z format) or press enter to skip: ")
    scheduled_for = scheduled_for_input if scheduled_for_input else None

    importance_input = input("importance (high/normal/low) or press enter to skip: ")
    importance = importance_input if importance_input and importance_input in ["high", "normal", "low"] else None

    cc_address_input = input("cc email address or press enter to skip: ")
    cc_address = cc_address_input if cc_address_input else None

    return notifications_client.send_email_notification(
        email_address,
        template_id=template_id,
        personalisation=personalisation,
        reference=reference,
        email_reply_to_id=email_reply_to_id,
        scheduled_for=scheduled_for,
        importance=importance,
        cc_address=cc_address,
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
    status = input("Notification status or press enter to skip: ")
    template_type = input("Notification template type or press enter to skip: ")
    reference = input("Notification reference or press enter to skip: ")
    older_than = input("Older than id or press enter to skip: ")
    return notifications_client.get_all_notifications(
        status=status, template_type=template_type, reference=reference, older_than=older_than
    )


def preview_template(notifications_client):
    template_id = input("Template id: ")
    personalisation = input("personalisation data: ")
    return notifications_client.post_template_preview(template_id, personalisation)


def get_template(notifications_client):
    template_id = input("Template id: ")
    return notifications_client.get_template(template_id)


def get_all_templates(notifications_client):
    template_type = input("template type or press enter to skip: ")
    return notifications_client.get_all_templates(template_type)


def get_template_version(notifications_client):
    template_id = input("Template id: ")
    version = input("Version: ")
    return notifications_client.get_template_version(template_id, version)


def send_bulk_notifications(notifications_client, **kwargs):
    # Récupérer les informations principales
    notification_type = kwargs.get("--type") or input("Enter type: email | sms: ")
    template_id = kwargs.get("--template-id") or input("Enter template id: ")
    name = kwargs.get("--name") or input("Enter name: ")
    reference = kwargs.get("--reference") or input("Enter reference: ")

    # Vérifier le type de notification (email ou sms)
    if notification_type not in ["email", "sms"]:
        print("Invalid notification type. Choose either 'email' or 'sms'.")
        sys.exit(1)

    # Demander quel type de données l'utilisateur souhaite envoyer : rows ou csv
    data_type = input("Do you want to send rows or csv data? (Enter 'rows' or 'csv'): ").strip().lower()

    # Exemple de champ selon le type de notification
    if notification_type == "email":
        field_example = "email address"  # Exemple pour email
        value_example = "user@example.com"  # Exemple de valeur pour email
    elif notification_type == "sms":
        field_example = "phone number"  # Exemple pour SMS
        value_example = "+12345023125"  # Exemple de valeur pour SMS

    # Vérification de l'entrée data_type
    if data_type == "rows":
        rows_data = input(
            f"Enter rows data for {notification_type}s "
            f'(e.g. [["{field_example}", "name"], ["{value_example}", "Alice"]]): '
        )
        print("rows_data :", rows_data)
        try:
            rows = json.loads(rows_data)  # Convertir en liste de listes
        except json.JSONDecodeError:
            print("Invalid --rows value. Must be a valid JSON list of lists.")
            sys.exit(1)
        return notifications_client.send_bulk_notifications(
            template_id=template_id,
            name=name,
            rows=rows,
            reference=reference,
        )

    elif data_type == "csv":
        csv_data = input(
            f"Enter csv data for {notification_type}s (e.g. '{field_example},name\\n{value_example},Alice'): "
        )
        csv_data = csv_data.replace("\\n", "\n")
        return notifications_client.send_bulk_notifications(
            template_id=template_id,
            name=name,
            csv=csv_data,
            reference=reference,
        )

    else:
        print("Invalid data type. Choose either 'rows' or 'csv'.")
        sys.exit(1)


def check_health(notifications_client):
    return notifications_client.check_health()


if __name__ == "__main__":
    arguments = docopt(__doc__)

    client = NotificationsAPIClient(
        base_url=arguments["<base_url>"], client_id=arguments["<client-id>"], api_key=arguments["<secret>"]
    )

    called_command = next(
        (
            cmd
            for cmd in [
                "health",
                "send-bulk",
                "create",
                "fetch",
                "fetch-all",
                "fetch-generator",
                "preview",
                "template",
                "all_templates",
                "template_version",
                "all_template_versions",
            ]
            if arguments[cmd]
        ),
        None,
    )

    match called_command:
        case "health":
            pprint(check_health(notifications_client=client))
        case "send-bulk":
            pprint(
                send_bulk_notifications(
                    notifications_client=client, **{k: arguments[k] for k in arguments if k.startswith("--")}
                )
            )
        case "create":
            pprint(
                create_notification(
                    notifications_client=client, **{k: arguments[k] for k in arguments if k.startswith("--")}
                )
            )
        case "fetch":
            pprint(get_notification(notifications_client=client))
        case "fetch-all":
            pprint(get_all_notifications(notifications_client=client))
        case "fetch-generator":
            pprint(list(get_all_notifications_generator(notifications_client=client)))
        case "preview":
            pprint(preview_template(notifications_client=client))
        case "template":
            pprint(get_template(notifications_client=client))
        case "all_templates":
            pprint(get_all_templates(notifications_client=client))
        case "template_version":
            pprint(get_template_version(notifications_client=client))
        case _:
            print("Commande non reconnue.")
