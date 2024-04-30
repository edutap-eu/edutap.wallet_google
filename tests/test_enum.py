def test_camel_case_alias_enum():
    from edutap.wallet_google.models.primitives.enums import CamelCaseAliasEnum

    class TestFoo(CamelCaseAliasEnum):
        FOO_BAR_BAZ = "FOO_BAR_BAZ"

    assert TestFoo("fooBarBaz") == TestFoo.FOO_BAR_BAZ


def test_action_enum():
    from edutap.wallet_google.models.primitives.enums import Action

    assert Action("ACTION_UNSPECIFIED") == Action.ACTION_UNSPECIFIED
    assert Action("actionUnspecified") == Action.ACTION_UNSPECIFIED

    assert Action("S2AP") != Action.ACTION_UNSPECIFIED

    assert Action("S2AP") == Action.S2AP
    assert Action("s2ap") == Action.S2AP

    assert Action("SIGN_UP") == Action.SIGN_UP
    assert Action("signUp") == Action.SIGN_UP
