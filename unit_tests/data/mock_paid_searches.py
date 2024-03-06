import datetime

from search_local_land_charge_api.models import PaidSearch

MOCK_PAID_SEARCHES = {
    '1': PaidSearch(search_id=1, user_id="test-user-id",
                    payment_id="test-payment-id", charges=[],
                    search_extent={"test": "extent"}, search_date=datetime.datetime.now(),
                    document_url="test-url", search_area_description='abc',
                    amount=10, card_brand="test_card", reference='abc', payment_provider="test_provider"),
    '2': PaidSearch(search_id=2, user_id="test-user-id",
                    payment_id="test-payment-id", charges=[],
                    search_extent={"test": "extent"}, search_date=datetime.datetime.now(),
                    document_url="test-url", search_area_description='abc',
                    amount=10, card_brand="test_card", reference='abc', payment_provider="test_provider")
}

MOCK_PAID_SEARCH_PAYLOAD = {
    "search_id": 1,
    "user_id": "test-user-id",
    "payment_id": "test-payment-id",
    "charges": [],
    "search_extent": {"test": "extent"},
    "search_date": datetime.datetime.now().isoformat(),
    "lapsed_date": None,
    "document_url": "test-url",
    "search_area_description": "abc",
    "amount": 10,
    "card_brand": "test_card",
    "reference": "abc",
    "payment_provider": "test_provider"
}

MOCK_ANONYMOUS_PAID_SEARCH_PAYLOAD = {
    "search_id": 1,
    "user_id": None,
    "payment_id": "test-payment-id",
    "charges": [],
    "search_extent": {"test": "extent"},
    "search_date": datetime.datetime.now().isoformat(),
    "lapsed_date": None,
    "document_url": "test-url",
    "search_area_description": "abc",
    "amount": 10,
    "card_brand": "test_card",
    "reference": "abc",
    "payment_provider": "test_provider"
}

MOCK_PAID_SEARCH_MISSING_SEARCH_ID_PAYLOAD = {
    "user_id": "test-user-id",
    "payment_id": "test-payment-id",
    "charges": [],
    "search_extent": {"test": "extent"},
    "search_date": datetime.datetime.now().isoformat(),
    "lapsed_date": None,
    "document_url": "test-url",
    "search_area_description": "abc",
    "amount": 10,
    "card_brand": "test_card",
    "reference": "abc",
    "payment_provider": "test_provider"
}
