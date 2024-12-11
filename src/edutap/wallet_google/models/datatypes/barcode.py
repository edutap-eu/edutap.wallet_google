from .enums import BarcodeRenderEncoding
from .enums import BarcodeType
from .enums import TotpAlgorithm
from .localized_string import LocalizedString
from pydantic import BaseModel


class Barcode(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/Barcode
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    type: BarcodeType = BarcodeType.BARCODE_TYPE_UNSPECIFIED
    renderEncoding: BarcodeRenderEncoding = (
        BarcodeRenderEncoding.RENDER_ENCODING_UNSPECIFIED
    )
    value: str | None = None
    alternateText: str | None = None
    showCodeText: LocalizedString | None = None


class TotpParameters(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/RotatingBarcode#totpparameters
    """

    key: str
    valueLength: int


class TotpDetails(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/RotatingBarcode#totpdetails
    """

    periodMillis: str
    algorithm: TotpAlgorithm = TotpAlgorithm.TOTP_ALGORITHM_UNSPECIFIED
    parameters: list[TotpParameters]


class RotatingBarcode(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/RotatingBarcode
    """

    type: BarcodeType = BarcodeType.BARCODE_TYPE_UNSPECIFIED
    renderEncoding: BarcodeRenderEncoding = (
        BarcodeRenderEncoding.RENDER_ENCODING_UNSPECIFIED
    )
    valuePattern: str | None = None
    totpDetails: TotpDetails | None = None
    alternateText: str | None = None
    showCodeText: LocalizedString | None = None
