from edutap.wallet_google import registry
from edutap.wallet_google.models import generic
from edutap.wallet_google.models import retail
from edutap.wallet_google.models import ticket_and_transit

import pytest


def test_registry():
    print(registry._MODEL_REGISTRY)
    assert len(registry._MODEL_REGISTRY)
    assert retail.LoyaltyObject in registry._MODEL_REGISTRY


@pytest.mark.parametrize(
    ["name", "cls"],
    [
        # retail
        ("GiftCardClass", retail.GiftCardClass),
        ("GiftCardObject", retail.GiftCardObject),
        ("LoyaltyClass", retail.LoyaltyClass),
        ("LoyaltyObject", retail.LoyaltyObject),
        ("OfferClass", retail.OfferClass),
        ("OfferObject", retail.OfferObject),
        # ticket and transit
        ("EventTicketClass", ticket_and_transit.EventTicketClass),
        ("EventTicketObject", ticket_and_transit.EventTicketObject),
        # generic
        ("GenericClass", generic.GenericClass),
        ("GenericObject", generic.GenericObject),
    ],
)
def test_lookup_model_by_name(name, cls):
    assert registry.lookup_model_by_name(name) == cls


@pytest.mark.parametrize(
    ["cls", "url_name"],
    [
        # retail
        (retail.GiftCardClass, "giftCardClass"),
        (retail.GiftCardObject, "giftCardObject"),
        (retail.LoyaltyClass, "loyaltyClass"),
        (retail.LoyaltyObject, "loyaltyObject"),
        (retail.OfferClass, "offerClass"),
        (retail.OfferObject, "offerObject"),
        # ticket and transit
        (ticket_and_transit.EventTicketClass, "eventTicketClass"),
        (ticket_and_transit.EventTicketObject, "eventTicketObject"),
        # generic
        (generic.GenericClass, "genericClass"),
        (generic.GenericObject, "genericObject"),
    ],
)
def test_lookup_url_name(cls, url_name):
    assert registry.lookup_url_name(cls=cls) == url_name


def test_lookup_url_name_on_unknown_model():
    with pytest.raises(LookupError):
        registry.lookup_url_name(cls=str)


@pytest.mark.parametrize(
    ["cls", "method", "return_value"],
    [
        # LoyaltyClass
        (retail.LoyaltyClass, registry.Capability.insert, True),
        (retail.LoyaltyClass, registry.Capability.get, True),
        (retail.LoyaltyClass, registry.Capability.update, True),
        (retail.LoyaltyClass, registry.Capability.patch, True),
        (retail.LoyaltyClass, registry.Capability.list, True),
        (retail.LoyaltyClass, registry.Capability.addmessage, True),
        # LoyaltyObject
        (retail.LoyaltyObject, registry.Capability.insert, True),
        (retail.LoyaltyObject, registry.Capability.get, True),
        (retail.LoyaltyObject, registry.Capability.update, True),
        (retail.LoyaltyObject, registry.Capability.patch, True),
        (retail.LoyaltyObject, registry.Capability.list, True),
        (retail.LoyaltyObject, registry.Capability.addmessage, True),
    ],
)
def test_capability(cls, method, return_value):
    assert registry.check_capability(cls, method) is return_value
