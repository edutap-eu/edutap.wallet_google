from ..bases import Model
from ..deprecated import DeprecatedKindFieldMixin
from .enums import BarcodeRenderEncoding, BarcodeType, TotpAlgorithm
from .localized_string import LocalizedString

# Attribute order as in Google's documentation to make future updates easier!
# last check: 2025-01-22


class Barcode(DeprecatedKindFieldMixin, Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/Barcode
    """

    # inherits kind (deprecated)
    type: BarcodeType = BarcodeType.BARCODE_TYPE_UNSPECIFIED
    renderEncoding: BarcodeRenderEncoding = (
        BarcodeRenderEncoding.RENDER_ENCODING_UNSPECIFIED
    )
    value: str | None = None
    alternateText: str | None = None
    showCodeText: LocalizedString | None = None


class TotpParameters(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/RotatingBarcode#totpparameters
    """

    key: str
    valueLength: int


class TotpDetails(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/RotatingBarcode#totpdetails
    """

    periodMillis: str
    algorithm: TotpAlgorithm = TotpAlgorithm.TOTP_ALGORITHM_UNSPECIFIED
    parameters: list[TotpParameters]


class RotatingBarcodeValues(Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/RotatingBarcode#rotatingbarcodevalues
    """

    startDateTime: str | None = None
    values: list[str] | None = None
    periodMillis: str | None = None


class RotatingBarcode(Model):
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
    initialRotatingBarcodeValues: RotatingBarcodeValues | None = None
