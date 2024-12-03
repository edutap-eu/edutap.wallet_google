from .primitives import CallbackOptions
from .primitives import GroupingInfo
from .primitives import Image
from .primitives import PassConstraints
from .primitives import SaveRestrictions
from .primitives import SecurityAnimation
from .primitives.barcode import Barcode
from .primitives.barcode import RotatingBarcode
from .primitives.class_template_info import ClassTemplateInfo
from .primitives.data import AppLinkData
from .primitives.data import ImageModuleData
from .primitives.data import InfoModuleData
from .primitives.data import LinksModuleData
from .primitives.data import TextModuleData
from .primitives.datetime import TimeInterval
from .primitives.enums import MultipleDevicesAndHoldersAllowedStatus
from .primitives.enums import State
from .primitives.enums import ViewUnlockRequirement
from .primitives.message import Message
from .primitives.moduledata import ValueAddedModuleData
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class GoogleWalletModel(BaseModel):
    """
    Base Model for all Google Wallet Models.

    Sets a model_config for all Google Wallet Models that enforce that all attributes must be explicitly modeled, and trying to set an unknown attribute would raise an Exception.
    This Follows the Zen of Python (PEP 20) --> Explicit is better than implicit.
    """

    model_config = ConfigDict(
        extra="forbid",
        # use_enum_values=True,
    )


class GoogleWalletWithIdModel(BaseModel):
    """
    Model for Google Wallet models with an identifier.
    """

    id: str


class GoogleWalletClassModel(GoogleWalletModel, GoogleWalletWithIdModel):
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

    # inherited id
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


class GoogleWalletObjectModel(GoogleWalletModel, GoogleWalletWithIdModel):
    """
    Base model for all Google Wallet Object models.

    Opposed to the GoogleWalletClassModel, this class does not represent the GenericObject.
    So, it does not act as a base model for all other wallet object types.
    It is just a base model with all attributes all Google Wallet Objects models have in common.
    """

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


class GoogleWalletObjectWithClassReferenceMixin(
    GoogleWalletModel, GoogleWalletWithIdModel
):
    """
    Mixin for all Google Wallet Object with a classReferences attribute, that reflects the whole class data.
    This mixin class is used as an identifier for the registry.
    """

    classReference: GoogleWalletClassModel | None = None


class GoogleWalletStyleableMixin:
    """
    Mixin for Google Wallet Classes/Objects that can be styled.
    """

    hexBackgroundColor: str | None = None


class GoogleWalletCommonLogosMixin:
    """
    Mixin for Google Wallet Classes/Objects with a common logo.

    Do not use/alias this mixin for Google Wallet Classes, as they have a different logo attribute.
    """

    logo: Image | None = None
    wideLogo: Image | None = None
    heroImage: Image | None = None
