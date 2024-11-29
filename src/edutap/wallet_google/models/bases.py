from .primitives import CallbackOptions
from .primitives import GroupingInfo
from .primitives import Image
from .primitives import PassConstraints
from .primitives import SecurityAnimation
from .primitives.barcode import Barcode
from .primitives.barcode import RotatingBarcode
from .primitives.class_template_info import ClassTemplateInfo
from .primitives.data import ImageModuleData
from .primitives.data import InfoModuleData
from .primitives.data import LinksModuleData
from .primitives.data import TextModuleData
from .primitives.enums import MultipleDevicesAndHoldersAllowedStatus
from .primitives.enums import ViewUnlockRequirement
from .primitives.message import Message
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
        # extra="ignore",
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
    """

    # Templating and Visual Data
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

    # Callback Options
    callbackOptions: CallbackOptions | None = None

    # Smarttap Options
    enableSmartTap: bool | None = None
    redemptionIssuers: list[str] | None = None  # string (int64 format)

    # Barcode Options
    securityAnimation: SecurityAnimation | None = None

    # Security Options
    viewUnlockRequirement: ViewUnlockRequirement = (
        ViewUnlockRequirement.VIEW_UNLOCK_REQUIREMENT_UNSPECIFIED
    )
    allowMultipleUsersPerObject: bool | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default=None,
    )
    multipleDevicesAndHoldersAllowedStatus: MultipleDevicesAndHoldersAllowedStatus = (
        MultipleDevicesAndHoldersAllowedStatus.STATUS_UNSPECIFIED
    )

    wordMark: Image | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default=None,
    )


class GoogleWalletObjectModel(GoogleWalletModel, GoogleWalletWithIdModel):
    """
    Base model for all Google Wallet Object models.
    """

    classId: str
    version: str | None = Field(
        description="deprecated", deprecated=True, exclude=True, default=None
    )

    groupingInfo: GroupingInfo | None = None

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


class GoogleWalletObjectWithClassReferenceMixin(
    GoogleWalletModel, GoogleWalletWithIdModel
):
    """
    Mixin for all Google Wallet Object with a classReferences attribute, that reflects the whole class data.
    """

    classReference: GoogleWalletClassModel | None = None


class GoogleWalletMessageableMixin:
    """
    Mixin for Google Wallet Classes or Objects that can retrieve Messages
    """

    messages: list[Message] | None = None


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
