from marshmallow import Schema, fields, post_dump, post_load, pre_load
from search_local_land_charge_api.models import PaidSearch


class PaidSearchSchema(Schema):
    search_id = fields.Int(required=True)
    user_id = fields.Str(required=True, allow_none=True)
    payment_id = fields.Str(required=True)
    charges = fields.List(fields.Dict(), allow_none=True)
    search_extent = fields.Dict(required=True)
    search_date = fields.DateTime(required=True)
    search_area_description = fields.Str(allow_none=True)
    lapsed_date = fields.DateTime(allow_none=True)
    document_url = fields.Str(allow_none=True)
    parent_search_id = fields.Int(allow_none=True)
    payment_provider = fields.Str(allow_none=True)
    card_brand = fields.Str(allow_none=True)
    amount = fields.Integer(allow_none=True)
    reference = fields.Str(allow_none=True)
    # Weird field that is sent in but artificially added back in response mapper
    repeat_searches = fields.List(fields.Dict(), allow_none=True, load_only=True)

    @pre_load
    def preload_process(self, data, **kwargs):
        return {
            key.replace('-', '_'): value for key, value in data.items()
        }

    @post_load
    def make_paid_search(self, data, **kwargs):
        # exclude lapsed_date and repeat_searches from object creation
        exclude_fields = {key: value for key, value in data.items() if key not in ['lapsed_date', 'repeat_searches']}
        return PaidSearch(**exclude_fields)

    @post_dump
    def postdump_process(self, data, **kwargs):
        return {
            key.replace('_', '-'): value for key, value in data.items()
        }
