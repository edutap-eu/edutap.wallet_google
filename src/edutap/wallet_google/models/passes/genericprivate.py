from ...registry import register_model
from ..bases import WithIdModel
from ..datatypes.barcode import Barcode
from ..datatypes.data import AppLinkData
from ..datatypes.data import LinksModuleData
from ..datatypes.data import TextModuleData
from ..datatypes.general import GroupingInfo
from ..datatypes.general import Image
from ..datatypes.localized_string import LocalizedString
from .bases import StyleableMixin

import enum


# Attribute order as in Google's documentation to make future updates easier!
# last check: 2024-10-16


class GenericPrivatePassType(enum.StrEnum):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/GenericPrivatePass
    """

    GENERIC_PRIVATE_PASS_TYPE_UNSPECIFIED = "GENERIC_PRIVATE_PASS_TYPE_UNSPECIFIED"


class SmartTapInfo(WithIdModel):
    enableSmartTap: bool = False
    redemptionIssuers: list[str] | None = None  # string (int64 format)
    smartTapRedemptionValue: str | None = None


@register_model(
    "GenericPrivatePass",
    url_part="privateContent",
    plural="GenericPrivatePasses",
    can_message=False,
)
class GenericPrivatePass(StyleableMixin, WithIdModel):

    type: GenericPrivatePassType = (
        GenericPrivatePassType.GENERIC_PRIVATE_PASS_TYPE_UNSPECIFIED
    )
    # inherits id
    # inherits hexBackgroundColor
    groupingInfo: GroupingInfo | None = None
    headerLogo: Image | None = None
    wideHeaderLogo: Image | None = None
    header: LocalizedString | None = None
    metaText: LocalizedString | None = None
    titleLabel: LocalizedString | None = None
    title: LocalizedString | None = None
    barcode: Barcode | None = None
    heroImage: Image | None = None
    textModulesData: list[TextModuleData] | None = None
    linksModuleData: list[LinksModuleData] | None = None
    appLinkData: AppLinkData | None = None
    smartTapInfo: SmartTapInfo | None = None
