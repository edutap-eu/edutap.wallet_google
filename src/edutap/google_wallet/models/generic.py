from ..registry import register_model
from ..registry import RegistrationType
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
from pydantic import BaseModel


@register_model(RegistrationType.WALLETCLASS, "genericClass")
class GenericClass(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/genericclass
    """

    id: str
    classTemplateInfo: ClassTemplateInfo | None
    imageModulesData: list[ImageModuleData] | None
    textModulesData: list[TextModuleData] | None
    linksModuleData: LinksModuleData | None
    enableSmartTap: bool = False
    redemptionIssuers: list[str] | None
    securityAnimation: SecurityAnimation | None
    multipleDevicesAndHoldersAllowedStatus: MultipleDevicesAndHoldersAllowedStatus | None = (
        MultipleDevicesAndHoldersAllowedStatus.STATUS_UNSPECIFIED
    )
    callbackOptions: CallbackOptions | None
    viewUnlockRequirement: ViewUnlockRequirement | None = (
        ViewUnlockRequirement.VIEW_UNLOCK_REQUIREMENT_UNSPECIFIED
    )


@register_model(RegistrationType.WALLETOBJECT, "genericObject")
class GenericObject(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/genericobject
    """

    id: str
    classId: str
    genericType: GenericType | None = GenericType.GENERIC_TYPE_UNSPECIFIED
    cardTitle: LocalizedString
    subheader: LocalizedString | None
    header: LocalizedString
    logo: Image | None
    hexBackgroundColor: str | None
    notifications: Notifications | None
    barcode: Barcode | None
    heroImage: Image | None
    validTimeInterval: TimeInterval | None
    imageModulesData: list[ImageModuleData] | None
    textModulesData: list[TextModuleData] | None
    linksModuleData: LinksModuleData | None
    appLinkData: AppLinkData | None
    groupingInfo: GroupingInfo | None
    smartTapRedemptionValue: str | None
    rotatingBarcode: RotatingBarcode | None
    state: State | None
    hasUsers: bool | None
    passConstraints: PassConstraints | None
