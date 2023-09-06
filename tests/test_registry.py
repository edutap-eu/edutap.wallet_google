import pytest


@pytest.fixture
def clean_registry():
    from edutap.wallet_google.registry import _REGISTRY
    from edutap.wallet_google.registry import RegistrationType

    OLD_CLASS_REGISTRY = _REGISTRY[RegistrationType.WALLETCLASS].copy()
    _REGISTRY[RegistrationType.WALLETCLASS].clear()
    OLD_OBJECT_REGISTRY = _REGISTRY[RegistrationType.WALLETOBJECT].copy()
    _REGISTRY[RegistrationType.WALLETOBJECT].clear()
    yield _REGISTRY
    _REGISTRY[RegistrationType.WALLETCLASS].clear()
    _REGISTRY[RegistrationType.WALLETCLASS].update(OLD_CLASS_REGISTRY)
    _REGISTRY[RegistrationType.WALLETOBJECT].clear()
    _REGISTRY[RegistrationType.WALLETOBJECT].update(OLD_OBJECT_REGISTRY)


def test_decorator(clean_registry):
    from edutap.wallet_google.registry import register_model
    from edutap.wallet_google.registry import RegistrationType

    @register_model(RegistrationType.WALLETOBJECT, "foo")
    class Foo:
        pass

    assert clean_registry[RegistrationType.WALLETOBJECT] == {"foo": Foo}

    with pytest.raises(ValueError):

        @register_model(RegistrationType.WALLETOBJECT, "foo")
        class AnotherFoo:
            pass

    @register_model(RegistrationType.WALLETCLASS, "foo")
    class Foo:
        pass

    assert clean_registry[RegistrationType.WALLETCLASS] == {"foo": Foo}


def test_lookup(clean_registry):
    from edutap.wallet_google.registry import register_model
    from edutap.wallet_google.registry import RegistrationType

    @register_model(RegistrationType.WALLETOBJECT, "foo")
    class Foo:
        pass

    from edutap.wallet_google.registry import lookup

    assert lookup(RegistrationType.WALLETOBJECT, "foo") == Foo

    with pytest.raises(KeyError):
        lookup(RegistrationType.WALLETOBJECT, "bar")
