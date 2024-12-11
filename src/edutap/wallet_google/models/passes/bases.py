from ..bases import WithIdModel
from ..datatypes.barcode import Barcode
from ..datatypes.barcode import RotatingBarcode
from ..datatypes.class_template_info import ClassTemplateInfo
from ..datatypes.data import AppLinkData
from ..datatypes.data import ImageModuleData
from ..datatypes.data import InfoModuleData
from ..datatypes.data import LinksModuleData
from ..datatypes.data import TextModuleData
from ..datatypes.datetime import TimeInterval
from ..datatypes.enums import MultipleDevicesAndHoldersAllowedStatus
from ..datatypes.enums import State
from ..datatypes.enums import ViewUnlockRequirement
from ..datatypes.general import CallbackOptions
from ..datatypes.general import GroupingInfo
from ..datatypes.general import Image
from ..datatypes.general import PassConstraints
from ..datatypes.general import SaveRestrictions
from ..datatypes.general import SecurityAnimation
from ..datatypes.message import Message
from ..datatypes.moduledata import ValueAddedModuleData
from pydantic import Field


class ClassModel(WithIdModel):
    """
    BaseModel for all Google Wallet Class Models.

    Even if not documented explicitly by Google, the GenericClass acts as
    the base-class for all Google Wallet Classes. So this here is the GenericClass.
    To keep the inheritance chain semantically clean, there is a registered GenericClass
    inheriting from here without any added attributes in the module `generic.py`.
    see https://developers.google.com/wallet/generic/rest/v1/genericclass
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-12-02

    # inherits id
    classTemplateInfo: ClassTemplateInfo | None = None
    imageModulesData: list[ImageModuleData] | None = None
    textModulesData: list[TextModuleData] | None = None
    linksModuleData: LinksModuleData | None = None
    infoModuleData: InfoModuleData | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default=None,
    )
    enableSmartTap: bool | None = None
    redemptionIssuers: list[str] | None = None  # string (int64 format)
    securityAnimation: SecurityAnimation | None = None
    multipleDevicesAndHoldersAllowedStatus: MultipleDevicesAndHoldersAllowedStatus = (
        MultipleDevicesAndHoldersAllowedStatus.STATUS_UNSPECIFIED
    )
    callbackOptions: CallbackOptions | None = None
    viewUnlockRequirement: ViewUnlockRequirement = (
        ViewUnlockRequirement.VIEW_UNLOCK_REQUIREMENT_UNSPECIFIED
    )
    messages: list[Message] | None = None
    appLinkData: AppLinkData | None = None
    valueAddedModuleData: ValueAddedModuleData | None = None


class ObjectModel(WithIdModel):
    """
    Base model for all Google Wallet Object models.

    Opposed to the ClassModel, this class does not represent the GenericObject.
    So, it does not act as a base model for all other wallet object types.
    It is just a base model with all attributes all Google Wallet Objects models have in common.
    """

    # inherits id
    classId: str
    version: str | None = Field(
        description="deprecated", deprecated=True, exclude=True, default=None
    )

    # Templating and Visual Data
    imageModulesData: list[ImageModuleData] | None = None
    textModulesData: list[TextModuleData] | None = None
    linksModuleData: LinksModuleData | None = None
    infoModuleData: InfoModuleData | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default=None,
    )

    # Security Options
    passConstraints: PassConstraints | None = None

    # Smart Tap Option
    smartTapRedemptionValue: str | None = None

    # Barcode Options
    barcode: Barcode | None = None
    rotatingBarcode: RotatingBarcode | None = None

    # other general
    groupingInfo: GroupingInfo | None = None
    saveRestrictions: SaveRestrictions | None = None
    linkedObjectIds: list[str] | None = None
    valueAddedModuleData: ValueAddedModuleData | None = None
    messages: list[Message] | None = None
    appLinkData: AppLinkData | None = None
    state: State = Field(default=State.STATE_UNSPECIFIED)
    hasUsers: bool | None = None
    validTimeInterval: TimeInterval | None = None


class ObjectWithClassReference(WithIdModel):
    """
    Mixin for all Google Wallet Object with a classReferences attribute, that reflects the whole class data.
    This class is used to create the save_link only, never inherit from it.
    """

    classReference: ClassModel | None = None


class StyleableMixin:
    """
    Mixin for Google Wallet Classes/Objects that can be styled.
    """

    hexBackgroundColor: str | None = None


class CommonLogosMixin:
    """
    Mixin for Google Wallet Classes/Objects with a common logo.

    Do not use/alias this mixin for Google Wallet Classes, as they have a different logo attribute.
    """

    logo: Image | None = None
    wideLogo: Image | None = None
    heroImage: Image | None = None