from ..modelbase import GoogleWalletClassModel
from ..modelbase import GoogleWalletObjectModel
from ..registry import register_model
from .primitives import CallbackOptions
from .primitives import GroupingInfo
from .primitives import Image
from .primitives import PassConstraints
from .primitives import SecurityAnimation
from .primitives.barcode import Barcode
from .primitives.barcode import RotatingBarcode
from .primitives.class_template_info import ClassTemplateInfo
from .primitives.data import AppLinkData
from .primitives.data import ImageModuleData
from .primitives.data import LinksModuleData
from .primitives.data import TextModuleData
from .primitives.datetime import TimeInterval
from .primitives.enums import GenericType
from .primitives.enums import MultipleDevicesAndHoldersAllowedStatus
from .primitives.enums import State
from .primitives.enums import ViewUnlockRequirement
from .primitives.localized_string import LocalizedString
from .primitives.notification import Notifications
from pydantic import Field


@register_model(
    "GenericClass", url_part="genericClass", plural="genericClass", can_disable=False
)
class GenericClass(GoogleWalletClassModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/genericclass
    """

    classTemplateInfo: ClassTemplateInfo | None = None
    imageModulesData: list[ImageModuleData] | None = None
    textModulesData: list[TextModuleData] | None = None
    linksModuleData: LinksModuleData | None = None
    enableSmartTap: bool = False
    redemptionIssuers: list[str] | None = None
    securityAnimation: SecurityAnimation | None = None
    multipleDevicesAndHoldersAllowedStatus: MultipleDevicesAndHoldersAllowedStatus = (
        Field(default=MultipleDevicesAndHoldersAllowedStatus.STATUS_UNSPECIFIED)
    )
    callbackOptions: CallbackOptions | None = None
    viewUnlockRequirement: ViewUnlockRequirement = Field(
        default=ViewUnlockRequirement.VIEW_UNLOCK_REQUIREMENT_UNSPECIFIED
    )


@register_model("GenericObject", url_part="genericObject")
class GenericObject(GoogleWalletObjectModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/genericobject
    """

    genericType: GenericType = GenericType.GENERIC_TYPE_UNSPECIFIED
    cardTitle: LocalizedString
    subheader: LocalizedString | None = None
    header: LocalizedString
    logo: Image | None = None
    hexBackgroundColor: str | None = None
    notifications: Notifications | None = None
    barcode: Barcode | None = None
    heroImage: Image | None = None
    validTimeInterval: TimeInterval | None = None
    imageModulesData: list[ImageModuleData] | None = None
    textModulesData: list[TextModuleData] | None = None
    linksModuleData: LinksModuleData | None = None
    appLinkData: AppLinkData | None = None
    groupingInfo: GroupingInfo | None = None
    smartTapRedemptionValue: str | None = None
    rotatingBarcode: RotatingBarcode | None = None
    state: State = Field(default=State.STATE_UNSPECIFIED)
    hasUsers: bool | None = None
    passConstraints: PassConstraints | None = None
