from jsf import JSF

from integration_test.schemas.v2.notification_schemas import post_bulk_notifications_response


def _merge_if_simple_or_inexistant(json_object, merged_dict):
    for key, value in merged_dict.items():
        if isinstance(value, str) or isinstance(value, int) or isinstance(value, float) or isinstance(value, bool) or value is None:
            json_object[key] = value
        else:
            if key in json_object:
                _merge_if_simple_or_inexistant(json_object[key], value)
            else:
                json_object[key] = value


class JSONBuilder:
    def __init__(self, json_object):
        self.json_object = json_object

    def override(self, **kwargs):
        self.json_object.update(kwargs)
        return self

    def merge_values(self, merged_dict: dict):
        _merge_if_simple_or_inexistant(self.json_object, merged_dict)

        return self

    def get_json_object(self):
        return self.json_object

    @staticmethod
    def from_schema(schema: dict):

        fakers = JSF(schema)
        return JSONBuilder(fakers.generate())

if __name__ == "__main__":
    object = JSONBuilder.from_schema(post_bulk_notifications_response).merge_values({"data" : {
        "notification_count": 2
    }}).get_json_object()

    print(object)