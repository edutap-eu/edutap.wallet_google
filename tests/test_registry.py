import copy
import pytest


@pytest.fixture
def clean_registry():
    from edutap.wallet_google.registry import _MODEL_REGISTRY

    OLD_MODEL_REGISTRY = copy.deepcopy(_MODEL_REGISTRY)
    _MODEL_REGISTRY.clear()
    yield _MODEL_REGISTRY
    _MODEL_REGISTRY.clear()
    _MODEL_REGISTRY.update(OLD_MODEL_REGISTRY)


def test_decorator(clean_registry):
    from edutap.wallet_google.registry import register_model

    @register_model("foo")
    class Foo:
        pass

    assert clean_registry["foo"] == {
        "can_create": True,
        "can_disable": True,
        "can_message": False,
        "can_read": True,
        "can_update": True,
        "model": Foo,
        "name": "foo",
        "url_part": "foo",
    }

    with pytest.raises(ValueError):

        @register_model("foo")
        class AnotherFoo:
            pass

    @register_model(
        "bar",
        url_part="baar",
        can_create=False,
        can_read=False,
        can_update=False,
        can_disable=False,
        can_message=True,
    )
    class Bar:
        pass

    assert clean_registry["bar"] == {
        "can_create": False,
        "can_disable": False,
        "can_message": True,
        "can_read": False,
        "can_update": False,
        "model": Bar,
        "name": "bar",
        "url_part": "baar",
    }


def test_lookup_model(clean_registry):
    from edutap.wallet_google.registry import register_model

    @register_model("foo")
    class Foo:
        pass

    from edutap.wallet_google.registry import lookup_model

    assert lookup_model("foo") == Foo

    with pytest.raises(KeyError):
        lookup_model("bar")


def test_lookup_metadata(clean_registry):
    from edutap.wallet_google.registry import register_model

    @register_model("foo")
    class Foo:
        pass

    from edutap.wallet_google.registry import lookup_metadata

    assert lookup_metadata("foo") == {
        "can_create": True,
        "can_disable": True,
        "can_message": False,
        "can_read": True,
        "can_update": True,
        "model": Foo,
        "name": "foo",
        "url_part": "foo",
    }

    with pytest.raises(KeyError):
        lookup_metadata("bar")


def test_raise_when_operation_not_allowed(clean_registry):
    from edutap.wallet_google.registry import register_model

    @register_model("foo")
    class Foo:
        pass

    from edutap.wallet_google.registry import raise_when_operation_not_allowed

    assert raise_when_operation_not_allowed("foo", "create") is None

    with pytest.raises(ValueError):
        raise_when_operation_not_allowed("foo", "message")
