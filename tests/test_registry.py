from edutap.wallet_google import registry
from edutap.wallet_google.models import retail

import pytest


@pytest.fixture
def clean_registry():
    from edutap.wallet_google.registry import _MODEL_REGISTRY

    OLD_REGISTRY = _MODEL_REGISTRY.copy()
    _MODEL_REGISTRY.clear()
    yield _MODEL_REGISTRY
    _MODEL_REGISTRY.update(OLD_REGISTRY)


def test_decorator(clean_registry):
    from edutap.wallet_google.registry import register_model

    @register_model("foo")
    class Foo:
        pass

    assert Foo in clean_registry.keys()
    assert len(clean_registry) == 1

    with pytest.raises(ValueError):

        @register_model("foo")
        class Foo:
            pass

    @register_model("foo")
    class Foo:
        pass

    assert Foo in clean_registry.keys()
    assert len(clean_registry) == 1


def test_lookup(clean_registry):
    from edutap.wallet_google.registry import register_model

    @register_model("foo")
    class Foo:
        pass

    class Bar:
        pass

    with pytest.raises(LookupError):
        registry.lookup_model(Bar)


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


def test_lookuo_url_name_on_unknown_model():
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
    ],
)
def test_capability(cls, method, return_value):
    assert registry.check_capability(cls, method) is return_value
