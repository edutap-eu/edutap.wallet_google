from ..bases import Model
from ..datatypes.localized_string import LocalizedString
from ..datatypes.money import Money
from pydantic import Field
from pydantic import model_validator


# Attribute order as in Google's documentation to make future updates easier!
# last check: 2025-01-22


class LoyaltyPointsBalance(Model):
    """
    data-type,
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyobject#LoyaltyPointsBalance
    """

    string: str | None = None
    int_: int | None = Field(alias="int", serialization_alias="int", default=None)
    double: float | None = None
    money: Money | None = None

    @model_validator(mode="after")
    def check_one_of(self) -> "LoyaltyPointsBalance":
        given_values = [
            val
            for val in (self.string, self.int_, self.double, self.money)
            if val is not None
        ]
        if len(given_values) == 0:
            raise ValueError("One of string, int, double, or money must be set")
        if len(given_values) > 1:
            raise ValueError("Only one of string, int, double, or money must be set")
        return self


class LoyaltyPoints(Model):
    """
    data-type,
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyobject#LoyaltyPoints
    """

    label: str | None = None
    balance: LoyaltyPointsBalance | None = None
    localizedLabel: LocalizedString | None = None
