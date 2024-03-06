from marshmallow import Schema, fields, post_dump, post_load, pre_load
from search_local_land_charge_api.models import ServiceMessage


class ServiceMessageSchema(Schema):
    id = fields.Int(required=False)
    message_name = fields.Str(required=True, allow_none=True)
    message_en = fields.Str(required=True, allow_none=True)
    message_cy = fields.Str(required=True, allow_none=True)
    hyperlink_message_en = fields.Str(required=False, allow_none=True)
    hyperlink_message_cy = fields.Str(required=False, allow_none=True)
    hyperlink_link_en = fields.Str(required=False, allow_none=True)
    hyperlink_link_cy = fields.Str(required=False, allow_none=True)
    message_expiry_date = fields.Date(required=False, allow_none=True)

    @pre_load
    def preload_process(self, data, **kwargs):
        return {
            key.replace('-', '_'): value for key, value in data.items()
        }

    @post_load
    def make_service_message(self, data, **kwargs):
        return ServiceMessage(**data)

    @post_dump
    def postdump_process(self, data, **kwargs):
        return {
            key.replace('_', '-'): value for key, value in data.items() if value is not None
        }
