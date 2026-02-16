from pydantic import Field

from ..bases import Model
from ..deprecated import DeprecatedKindFieldMixin

# Attribute order as in Google's documentation to make future updates easier!
# last check: 2025-06-19


class LatLongPoint(DeprecatedKindFieldMixin, Model):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/LatLongPoint
    """

    # inherits kind (deprecated)
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)


class MerchantLocation(Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/MerchantLocation
    """

    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)
