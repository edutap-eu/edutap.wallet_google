from . import LocalizedString
from .enums import BarcodeRenderEncoding
from .enums import BarcodeType
from .enums import TotpAlgorithm
from pydantic import BaseModel
from typing import Optional


class Barcode(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/Barcode
    """

    kind: Optional[str] = "walletobjects#barcode"
    type: Optional[BarcodeType] | None = BarcodeType.BARCODE_TYPE_UNSPECIFIED
    renderEncoding: Optional[
        BarcodeRenderEncoding
    ] | None = BarcodeRenderEncoding.RENDER_ENCODING_UNSPECIFIED
    value: Optional[str]
    alternateText: Optional[str]
    showCodeText: Optional[LocalizedString]


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

    type: Optional[BarcodeType] = BarcodeType.BARCODE_TYPE_UNSPECIFIED
    renderEncoding: Optional[
        BarcodeRenderEncoding
    ] = BarcodeRenderEncoding.RENDER_ENCODING_UNSPECIFIED
    valuePattern: Optional[str]
    totpDetails: Optional[TotpDetails]
    alternateText: Optional[str]
    showCodeText: Optional[LocalizedString]
