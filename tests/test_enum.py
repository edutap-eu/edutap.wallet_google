import pytest


def test_camel_case_alias_enum():
    from edutap.wallet_google.models.bases import CamelCaseAliasEnum

    class TestFoo(CamelCaseAliasEnum):
        FOO_BAR_BAZ = "FOO_BAR_BAZ"

    assert TestFoo("FOO_BAR_BAZ") == TestFoo.FOO_BAR_BAZ
    assert TestFoo("fooBarBaz") == TestFoo.FOO_BAR_BAZ
    assert TestFoo("fooBarBaz") == "FOO_BAR_BAZ"
    with pytest.raises(ValueError):
        assert TestFoo("fooBarBaz") == "wrong"

    # test for https://github.com/edutap-eu/edutap.wallet_google/issues/12
    assert (
        repr(TestFoo("fooBarBaz")) == "<TestFoo.TestFoo camel case alias: 'fooBarBaz'>"
    )
    assert repr(TestFoo("FOO_BAR_BAZ")) == "<TestFoo.FOO_BAR_BAZ: 'FOO_BAR_BAZ'>"


def test_action_enum():
    from edutap.wallet_google.models.datatypes.enums import Action

    assert Action("ACTION_UNSPECIFIED") == Action.ACTION_UNSPECIFIED
    assert Action("actionUnspecified") == Action.ACTION_UNSPECIFIED

    assert Action("S2AP") != Action.ACTION_UNSPECIFIED

    assert Action("S2AP") == Action.S2AP
    assert Action("s2ap") == Action.S2AP

    assert Action("SIGN_UP") == Action.SIGN_UP
    assert Action("signUp") == Action.SIGN_UP


def test_pydantic_constraints():
    from edutap.wallet_google.models.bases import CamelCaseAliasEnum

    import pydantic

    class TestFoo(CamelCaseAliasEnum):
        FOO_BAR_BAZ = "FOO_BAR_BAZ"

    class TestModel(pydantic.BaseModel):
        foo: TestFoo = TestFoo.FOO_BAR_BAZ

    # accept snake case enum
    TestModel(foo=TestFoo("FOO_BAR_BAZ"))

    # accept snake case string
    TestModel(foo="FOO_BAR_BAZ")

    # accept camel case enum
    TestModel(foo=TestFoo("fooBarBaz"))

    # accept camel case string
    TestModel(foo="fooBarBaz")

    with pytest.raises(pydantic.ValidationError):
        TestModel(foo="wrong")


def test_camel_case_alias_enum_with_explicit_aliases():
    """Aliases that no rule derives from the canonical value.

    Google publishes deprecated legacy spellings next to the canonical enum
    values. Most of them are the plain camelCase form and are generated, but a
    few follow no rule at all (``EAN13`` for ``EAN_13``, ``qrcode`` for
    ``QR_CODE``). Those have to be spelled out.
    """
    from edutap.wallet_google.models.bases import CamelCaseAliasEnum

    class TestFoo(CamelCaseAliasEnum):
        FOO_BAR_BAZ = "FOO_BAR_BAZ", "FOOBARBAZ", "foobarbaz"

    assert TestFoo.FOO_BAR_BAZ.value == "FOO_BAR_BAZ"
    assert TestFoo("FOO_BAR_BAZ") == TestFoo.FOO_BAR_BAZ
    # the generated camelCase alias still works
    assert TestFoo("fooBarBaz") == TestFoo.FOO_BAR_BAZ
    # ... and so do the explicit ones
    assert TestFoo("FOOBARBAZ") == TestFoo.FOO_BAR_BAZ
    assert TestFoo("foobarbaz") == TestFoo.FOO_BAR_BAZ
    with pytest.raises(ValueError):
        TestFoo("unrelated")


def test_barcode_type_accepts_googles_legacy_spellings():
    """The Wallet API may send these; reading a response must not fail on them."""
    from edutap.wallet_google.models.datatypes.enums import ActivationState
    from edutap.wallet_google.models.datatypes.enums import BarcodeType

    assert BarcodeType("EAN13") == BarcodeType.EAN_13
    assert BarcodeType("PDF417") == BarcodeType.PDF_417
    assert BarcodeType("qrcode") == BarcodeType.QR_CODE
    assert ActivationState("not_activated") == ActivationState.NOT_ACTIVATED
