from search_local_land_charge_api.schema.paid_search_schema import \
    PaidSearchSchema


def map_paid_search_response(paid_searches):
    parent_searches = list(filter(lambda parent_search: parent_search.parent_search_id is None, paid_searches))
    repeat_searches = list(filter(lambda repeat_search: repeat_search.parent_search_id is not None, paid_searches))

    if parent_searches:
        return build_parent_searches_dict(parent_searches, repeat_searches)

    return build_repeat_searches_dict(repeat_searches)


def build_parent_searches_dict(parent_searches, repeat_searches):
    serialised_repeat_searches = build_repeat_searches_dict(repeat_searches)

    return list(map(lambda parent_search:
                    serialise_parent_searches(parent_search, serialised_repeat_searches), parent_searches))


def build_repeat_searches_dict(repeat_searches):
    return list(map(lambda repeat_search: serialise_paid_search(repeat_search), repeat_searches))


def serialise_paid_search(paid_search):
    paid_search_dict = PaidSearchSchema().dump(paid_search)
    if not paid_search_dict['parent-search-id']:
        paid_search_dict.pop('parent-search-id', None)

    return paid_search_dict


def serialise_parent_searches(parent_search, repeat_searches):
    parent_search_dict = serialise_paid_search(parent_search)
    parent_search_dict['repeat-searches'] = list(filter(
        lambda repeated_search:
        repeated_search["parent-search-id"] == parent_search_dict["search-id"], repeat_searches))
    return parent_search_dict
