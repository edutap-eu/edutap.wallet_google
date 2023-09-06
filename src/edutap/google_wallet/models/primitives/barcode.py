from . import LocalizedString
from .enums import BarcodeRenderEncoding
from .enums import BarcodeType
from .enums import TotpAlgorithm
from pydantic import BaseModel


class Barcode(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/Barcode
    """

    kind: str | None = "walletobjects#barcode"
    type: BarcodeType | None | None = BarcodeType.BARCODE_TYPE_UNSPECIFIED
    renderEncoding: BarcodeRenderEncoding | None = (
        BarcodeRenderEncoding.RENDER_ENCODING_UNSPECIFIED
    )
    value: str | None
    alternateText: str | None
    showCodeText: LocalizedString | None


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

    type: BarcodeType | None = BarcodeType.BARCODE_TYPE_UNSPECIFIED
    renderEncoding: BarcodeRenderEncoding | None = (
        BarcodeRenderEncoding.RENDER_ENCODING_UNSPECIFIED
    )
    valuePattern: str | None
    totpDetails: TotpDetails | None
    alternateText: str | None
    showCodeText: LocalizedString | None
