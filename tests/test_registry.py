from edutap.wallet_google import registry

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
