from ...modelcore import GoogleWalletWithKindModel
from pydantic import Field


class LatLongPoint(GoogleWalletWithKindModel):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/LatLongPoint
    """

    kind: str | None = Field(
        description="deprecated",
        exclude=True,
        default="walletobjects#latLongPoint",
    )
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)
