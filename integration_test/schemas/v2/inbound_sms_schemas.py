from integration_test.schemas.v2.definitions import uuid

get_inbound_sms_single_response = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "GET inbound sms schema response",
    "type": "object",
    "title": "GET response v2/inbound_sms",
    "properties": {
        "user_number": {"type": "string"},
        "created_at": {"format": "date-time", "type": "string", "description": "Date+time created at"},
        "service_id": uuid,
        "id": uuid,
        "notify_number": {"type": "string"},
        "content": {"type": "string"},
    },
    "required": ["id", "user_number", "created_at", "service_id", "notify_number", "content"],
    "additionalProperties": False,
}
