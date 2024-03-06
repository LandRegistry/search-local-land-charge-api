from marshmallow import Schema, fields, post_load
from search_local_land_charge_api.models import SearchStatusSearch


class SearchQuerySchema(Schema):
    id = fields.Int(required=True)
    request_timestamp = fields.DateTime(required=True)
    userid = fields.Str(required=True)
    status = fields.Str(required=True)
    completion_timestamp = fields.DateTime(required=False, allow_none=False)
    document = fields.Str(required=False, allow_none=False)
    external_url = fields.Str(required=False, allow_none=False)

    @post_load
    def make_search_status_search(self, data, **kwargs):
        return SearchStatusSearch(**data)
