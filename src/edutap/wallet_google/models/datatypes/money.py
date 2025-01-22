from ..bases import Model
from ..deprecated import DeprecatedKindFieldMixin


# Attribute order as in Google's documentation to make future updates easier!
# last check: 2025-01-22


class Money(DeprecatedKindFieldMixin, Model):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/Money
    """

    # inherits kind (deprecated)
    micros: str | None = None
    currencyCode: str | None = None
