from marshmallow import Schema, fields, post_dump, post_load, pre_load
from search_local_land_charge_api.models import FreeSearch


class FreeSearchSchema(Schema):
    _id = fields.Int(dump_only=True, data_key="id")
    user_id = fields.Str(required=True, allow_none=True)
    charge_ids = fields.List(fields.Integer(), required=True)
    search_extent = fields.Dict(required=True)
    search_date = fields.DateTime(required=True)
    address = fields.Str(required=False, allow_none=True)

    @pre_load
    def preload_process(self, data, **kwargs):
        return {
            key.replace('-', '_'): value for key, value in data.items()
        }

    @post_load
    def make_free_search(self, data, **kwargs):
        return FreeSearch(**data)

    @post_dump
    def postdump_process(self, data, **kwargs):
        return {
            key.replace('_', '-'): value for key, value in data.items()
        }
