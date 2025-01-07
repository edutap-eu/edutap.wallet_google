import pytest


def test_decorator(clean_registry_by_name, clean_registry_by_model):
    from edutap.wallet_google.registry import register_model

    @register_model("Foo", url_part="foo")
    class Foo:
        pass

    expected = {
        "can_create": True,
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
    assert clean_registry_by_name["Foo"] == expected
    assert clean_registry_by_model[Foo] == expected

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
        can_list=False,
        can_message=False,
    )
    class Bar:
        pass

    expected = {
        "can_create": False,
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
    assert clean_registry_by_name["Bar"] == expected
    assert clean_registry_by_model[Bar] == expected


def test_lookup_model_by_name(clean_registry_by_name, clean_registry_by_model):
    from edutap.wallet_google.registry import register_model

    @register_model("Foo", url_part="foo")
    class Foo:
        pass

    from edutap.wallet_google.registry import lookup_model_by_name

    assert lookup_model_by_name("Foo") == Foo

    with pytest.raises(KeyError):
        lookup_model_by_name("Bar")


def test_lookup_metadata_by_name(clean_registry_by_name, clean_registry_by_model):
    from edutap.wallet_google.registry import register_model

    @register_model("Foo", url_part="foo")
    class Foo:
        pass

    from edutap.wallet_google.registry import lookup_metadata_by_name

    assert lookup_metadata_by_name("Foo") == {
        "plural": "foos",
        "resource_id": "id",
        "can_create": True,
        "can_list": True,
        "can_message": True,
        "can_read": True,
        "can_update": True,
        "model": Foo,
        "name": "Foo",
        "url_part": "foo",
    }

    with pytest.raises(KeyError):
        lookup_metadata_by_name("Bar")


def test_lookup_metadata_by_model_instance(
    clean_registry_by_name, clean_registry_by_model
):
    from edutap.wallet_google.registry import register_model

    @register_model("Foo", url_part="foo")
    class Foo:
        pass

    foo = Foo()

    from edutap.wallet_google.registry import lookup_metadata_by_model_instance

    assert lookup_metadata_by_model_instance(foo) == {
        "plural": "foos",
        "resource_id": "id",
        "can_create": True,
        "can_list": True,
        "can_message": True,
        "can_read": True,
        "can_update": True,
        "model": Foo,
        "name": "Foo",
        "url_part": "foo",
    }

    class Bar:
        pass

    bar = Bar()

    with pytest.raises(KeyError):
        lookup_metadata_by_model_instance(bar)


def test_raise_when_operation_not_allowed(
    clean_registry_by_name, clean_registry_by_model
):
    from edutap.wallet_google.registry import register_model

    @register_model("foo", url_part="foo", can_message=False)
    class Foo:
        pass

    from edutap.wallet_google.registry import raise_when_operation_not_allowed

    assert raise_when_operation_not_allowed("foo", "create") is None

    with pytest.raises(ValueError):
        raise_when_operation_not_allowed("foo", "message")


def test_lookup_model_by_plural_name(clean_registry_by_name):
    from edutap.wallet_google.registry import register_model

    @register_model("Foo", url_part="foo", plural="fooos")
    class Foo:
        pass

    from edutap.wallet_google.registry import lookup_model_by_plural_name

    assert lookup_model_by_plural_name("fooos") == Foo

    with pytest.raises(LookupError):
        lookup_model_by_plural_name("barses")


def test_lookup_metadata_by_model_type(clean_registry_by_model):
    from edutap.wallet_google.registry import register_model

    @register_model("Foo", url_part="foo", plural="foos")
    class Foo:
        pass

    from edutap.wallet_google.registry import lookup_metadata_by_model_type

    md = lookup_metadata_by_model_type(Foo)
    assert md["name"] == "Foo"
    assert md["url_part"] == "foo"
    assert md["plural"] == "foos"
