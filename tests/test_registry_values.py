from edutap.wallet_google import registry
from edutap.wallet_google.models import retail

import pytest


def test_registry():
    print(registry._MODEL_REGISTRY)
    assert len(registry._MODEL_REGISTRY)
    assert retail.LoyaltyObject in registry._MODEL_REGISTRY


@pytest.mark.parametrize(
    ["cls", "url_name"],
    [
        (retail.LoyaltyClass, "loyaltyClass"),
        (retail.LoyaltyObject, "loyaltyObject"),
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
