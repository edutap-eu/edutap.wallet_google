import pytest


def test_decorator(clean_registry):
    from edutap.wallet_google.registry import register_model

    @register_model("Foo", url_part="foo")
    class Foo:
        pass

    assert clean_registry["Foo"] == {
        "can_create": True,
        "can_disable": True,
        "can_list": True,
        "can_message": True,
        "can_read": True,
        "can_update": True,
        "model": Foo,
        "name": "Foo",
        "plural": "foos",
        "resource_id": "id",
        "url_part": "foo",
    }

    with pytest.raises(ValueError):

        @register_model("Foo", url_part="foo")
        class AnotherFoo:
            pass

    @register_model(
        "Bar",
        url_part="baar",
        plural="barses",
        can_create=False,
        can_read=False,
        can_update=False,
        can_disable=False,
        can_list=False,
        can_message=False,
    )
    class Bar:
        pass

    assert clean_registry["Bar"] == {
        "can_create": False,
        "can_disable": False,
        "can_list": False,
        "can_message": False,
        "can_read": False,
        "can_update": False,
        "model": Bar,
        "name": "Bar",
        "plural": "barses",
        "resource_id": "id",
        "url_part": "baar",
    }


def test_lookup_model(clean_registry):
    from edutap.wallet_google.registry import register_model

    @register_model("Foo", url_part="foo")
    class Foo:
        pass

    from edutap.wallet_google.registry import lookup_model

    assert lookup_model("Foo") == Foo

    with pytest.raises(KeyError):
        lookup_model("Bar")


def test_lookup_metadata(clean_registry):
    from edutap.wallet_google.registry import register_model

    @register_model("Foo", url_part="foo")
    class Foo:
        pass

    from edutap.wallet_google.registry import lookup_metadata

    assert lookup_metadata("Foo") == {
        "plural": "foos",
        "resource_id": "id",
        "can_create": True,
        "can_disable": True,
        "can_list": True,
        "can_message": True,
        "can_read": True,
        "can_update": True,
        "model": Foo,
        "name": "Foo",
        "url_part": "foo",
    }

    with pytest.raises(KeyError):
        lookup_metadata("Bar")


def test_raise_when_operation_not_allowed(clean_registry):
    from edutap.wallet_google.registry import register_model

    @register_model("foo", url_part="foo", can_message=False)
    class Foo:
        pass

    from edutap.wallet_google.registry import raise_when_operation_not_allowed

    assert raise_when_operation_not_allowed("foo", "create") is None

    with pytest.raises(ValueError):
        raise_when_operation_not_allowed("foo", "message")
