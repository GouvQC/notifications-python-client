from integration_test.schemas.v2.definitions import https_url, personalisation, uuid

template = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "template schema",
    "type": "object",
    "title": "notification content",
    "properties": {"id": uuid, "version": {"type": "integer"}, "uri": {"type": "string"}},
    "required": ["id", "version", "uri"],
}

get_notification_response = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "GET notification response schema",
    "type": "object",
    "title": "response v2/notification",
    "properties": {
        "id": uuid,
        "reference": {"type": ["string", "null"]},
        "email_address": {"type": ["string", "null"]},
        "phone_number": {"type": ["string", "null"]},
        "line_1": {"type": ["string", "null"]},
        "line_2": {"type": ["string", "null"]},
        "line_3": {"type": ["string", "null"]},
        "line_4": {"type": ["string", "null"]},
        "line_5": {"type": ["string", "null"]},
        "line_6": {"type": ["string", "null"]},
        "postcode": {"type": ["string", "null"]},
        "postage": {"enum": ["first", "second", None]},
        "type": {"enum": ["sms", "email"]},
        "status": {"type": "string"},
        "template": template,
        "body": {"type": "string"},
        "subject": {"type": ["string", "null"]},
        "created_at": {"type": "string"},
        "sent_at": {"type": ["string", "null"]},
        "completed_at": {"type": ["string", "null"]},
        "created_by_name": {"type": ["string", "null"]},
    },
    "required": [
        # technically, all keys are required since we always have all of them
        "id",
        "reference",
        "email_address",
        "phone_number",
        "line_1",
        "line_2",
        "line_3",
        "line_4",
        "line_5",
        "line_6",
        "postcode",
        "type",
        "status",
        "template",
        "body",
        "created_at",
        "sent_at",
        "completed_at",
    ],
}

get_notifications_response = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "GET list of notifications response schema",
    "type": "object",
    "properties": {
        "notifications": {"type": "array", "items": {"type": "object", "ref": get_notification_response}},
        "links": {
            "type": "object",
            "properties": {"current": {"type": "string"}, "next": {"type": "string"}},
            "additionalProperties": False,
            "required": ["current"],
        },
    },
    "additionalProperties": False,
    "required": ["notifications", "links"],
}

post_sms_request = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST sms notification schema",
    "type": "object",
    "title": "POST v2/notifications/sms",
    "properties": {
        "reference": {"type": "string"},
        "phone_number": {"type": "string", "format": "phone_number"},
        "template_id": uuid,
        "sms_sender_id": uuid,
        "personalisation": personalisation,
    },
    "required": ["phone_number", "template_id"],
}

sms_content = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "content schema for SMS notification response schema",
    "type": "object",
    "title": "notification content",
    "properties": {"body": {"type": "string"}, "from_number": {"type": ["string", "null"]}},
    "required": ["body"],
}

post_sms_response = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST sms notification response schema",
    "type": "object",
    "title": "response v2/notifications/sms",
    "properties": {
        "id": uuid,
        "reference": {"type": ["string", "null"]},
        "content": sms_content,
        "uri": {"type": "string"},
        "template": template,
    },
    "required": ["id", "content", "uri", "template"],
}

post_email_request = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST email notification schema",
    "type": "object",
    "title": "POST v2/notifications/email",
    "properties": {
        "reference": {"type": "string"},
        "email_address": {"type": "string", "format": "email_address"},
        "template_id": uuid,
        "email_reply_to_id": uuid,
        "personalisation": personalisation,
        "one_click_unsubscribe_url": https_url,
    },
    "required": ["email_address", "template_id"],
}

email_content = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "Email content for POST email notification",
    "type": "object",
    "title": "notification email content",
    "properties": {
        "from_email": {"type": "string", "format": "email_address"},
        "body": {"type": "string"},
        "subject": {"type": "string"},
    },
    "required": ["body", "from_email", "subject"],
}

post_email_response = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST email notification response schema",
    "type": "object",
    "title": "response v2/notifications/email",
    "properties": {
        "id": uuid,
        "reference": {"type": ["string", "null"]},
        "content": email_content,
        "uri": {"type": "string"},
        "template": template,
    },
    "required": ["id", "content", "uri", "template"],
}

post_bulk_notifications_response = {
    "description": "Réponse de la route permettant de créer ou envoyer une notification en masse",
    "type": "object",
    "properties": {
        "data": {
            "type": "object",
            "description": "Données du job créé ou envoyé",
            "properties": {
                "id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "Identifiant unique du job",
                },
                "api_key": {
                    "type": "object",
                    "description": "Détails de la clé API utilisée pour ce job",
                    "properties": {
                        "id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Identifiant de la clé API",
                        },
                        "key_type": {
                            "type": "string",
                            "enum": ["team", "live", "test"],
                            "description": "Type de la clé API",
                        },
                        "name": {
                            "type": "string",
                            "description": "Nom de la clé API",
                        },
                    },
                    "required": ["id", "key_type", "name"],
                },
                "archived": {
                    "type": "boolean",
                    "description": "Indique si le job est archivé",
                },
                "created_at": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Horodatage de la création du job",
                },
                "updated_at": {
                    "type": ["string", "null"],
                    "format": "date-time",
                    "description": "Horodatage de la dernière mise à jour du job",
                },
                "created_by": {
                    "type": "object",
                    "description": "Informations sur l'utilisateur ayant créé le job",
                    "properties": {
                        "id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Identifiant de l'utilisateur",
                        },
                        "name": {
                            "type": "string",
                            "description": "Nom de l'utilisateur",
                        },
                    },
                    "required": ["id", "name"],
                },
                "job_status": {
                    "type": "string",
                    "enum": ["pending", "in-progress", "completed", "failed"],
                    "description": "Statut du job",
                },
                "notification_count": {
                    "type": "integer",
                    "description": "Nombre de notifications générées par le job",
                },
                "original_file_name": {
                    "type": "string",
                    "description": "Nom du fichier utilisé pour le job",
                },
                "processing_started": {
                    "type": ["string", "null"],
                    "format": "date-time",
                    "description": "Horodatage du début du traitement",
                },
                "processing_finished": {
                    "type": ["string", "null"],
                    "format": "date-time",
                    "description": "Horodatage de la fin du traitement",
                },
                "scheduled_for": {
                    "type": ["string", "null"],
                    "format": "date-time",
                    "description": "Date et heure de planification du job",
                },
                "sender_id": {
                    "type": ["string", "null"],
                    "format": "uuid",
                    "description": "Identifiant de l'expéditeur",
                },
                "service": {
                    "type": "string",
                    "format": "uuid",
                    "description": "Identifiant du service associé au job",
                },
                "service_name": {
                    "type": "object",
                    "description": "Nom du service associé au job",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Nom du service",
                        },
                    },
                    "required": ["name"],
                },
                "template": {
                    "type": "string",
                    "format": "uuid",
                    "description": "Identifiant du gabarit utilisé pour le job",
                },
                "template_version": {
                    "type": "integer",
                    "description": "Version du gabarit utilisé",
                },
            },
            "required": [
                "id", "api_key", "archived", "created_at", "created_by",
                "job_status", "notification_count", "original_file_name",
                "service", "service_name", "template", "template_version"
            ],
        }
    },
    "required": ["data"],
    "additionalProperties": False,
}


def create_post_sms_response_from_notification(notification, body, from_number, url_root):
    return {
        "id": notification.id,
        "reference": notification.client_reference,
        "content": {"body": body, "from_number": from_number},
        "uri": f"{url_root}/v2/notifications/{str(notification.id)}",
        "template": __create_template_from_notification(notification=notification, url_root=url_root),
    }


def create_post_email_response_from_notification(notification, content, subject, email_from, url_root):
    return {
        "id": notification.id,
        "reference": notification.client_reference,
        "content": {"from_email": email_from, "body": content, "subject": subject},
        "uri": f"{url_root}/v2/notifications/{str(notification.id)}",
        "template": __create_template_from_notification(notification=notification, url_root=url_root),
    }


def __create_template_from_notification(notification, url_root):
    return {
        "id": notification.template_id,
        "version": notification.template_version,
        "uri": f"{url_root}/v2/templates/{str(notification.template_id)}",
    }
