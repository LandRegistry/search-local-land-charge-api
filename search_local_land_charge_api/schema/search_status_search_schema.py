from marshmallow import Schema, fields, post_load
from search_local_land_charge_api.models import SearchStatusSearch


class SearchStatusSearchSchema(Schema):
    search_date = fields.DateTime(required=True)
    organisation = fields.Str(required=True)
    display_name = fields.Str(required=True)
    charge_ids = fields.List(fields.Str(), required=True)
    search_extent = fields.Dict(required=True)

    @post_load
    def make_free_search(self, data, **kwargs):
        return SearchStatusSearch(**data)
