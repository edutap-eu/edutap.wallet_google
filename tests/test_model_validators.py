import pytest


def test_reference_validator_missing():
    from edutap.wallet_google.models.passes.bases import Reference

    import pydantic

    with pytest.raises(pydantic.ValidationError):
        Reference(id="1234")


def test_reference_validator_both():
    from edutap.wallet_google.models.passes.bases import Reference
    from edutap.wallet_google.models.passes.generic import GenericObject

    import pydantic

    with pytest.raises(pydantic.ValidationError):
        Reference(id="1234", model_name="GenericObject", model_type=GenericObject)


def test_loyality_LoyaltyPointsBalance_validator_OK():
    from edutap.wallet_google.models.datatypes.loyalty import LoyaltyPointsBalance
    from edutap.wallet_google.models.datatypes.money import Money

    LoyaltyPointsBalance(string="1234")
    LoyaltyPointsBalance(int=1234)
    LoyaltyPointsBalance(double=1234.00)
    LoyaltyPointsBalance(money=Money(micros="123400", currencyCode="USD"))


def test_loyality_LoyaltyPointsBalance_validator_failures():
    from edutap.wallet_google.models.datatypes.loyalty import LoyaltyPointsBalance
    from edutap.wallet_google.models.datatypes.money import Money

    import pydantic

    # at least one
    with pytest.raises(pydantic.ValidationError):
        LoyaltyPointsBalance()

    # not 2
    with pytest.raises(pydantic.ValidationError):
        LoyaltyPointsBalance(int=1234, string="1234")

    # not 3
    with pytest.raises(pydantic.ValidationError):
        LoyaltyPointsBalance(int=1234, string="1234", double=1234.00)

    # not 4
    with pytest.raises(pydantic.ValidationError):
        LoyaltyPointsBalance(
            int=1234,
            string="1234",
            double=1234.00,
            money=Money(
                micros="123400",
                currencyCode="USD",
            ),
        )
