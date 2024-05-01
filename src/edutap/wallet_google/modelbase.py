from .modelcore import GoogleWalletModel
from .modelcore import GoogleWalletWithIdModel
from .models.primitives import CallbackOptions
from .models.primitives import GroupingInfo
from .models.primitives import Image
from .models.primitives import PassConstraints
from .models.primitives import SecurityAnimation
from .models.primitives.barcode import Barcode
from .models.primitives.barcode import RotatingBarcode
from .models.primitives.class_template_info import ClassTemplateInfo
from .models.primitives.data import ImageModuleData
from .models.primitives.data import InfoModuleData
from .models.primitives.data import LinksModuleData
from .models.primitives.data import TextModuleData
from .models.primitives.enums import MultipleDevicesAndHoldersAllowedStatus
from .models.primitives.enums import ViewUnlockRequirement
from .models.primitives.message import Message
from pydantic import Field


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

    # Design Options
    # hexBackgroundColor: str | None = None
    # logo: Image | None = None
    # wideLogo: Image | None = None
    # heroImage: Image | None = None
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


class GoogleWalletStyleableClassMixin:
    """
    Mixin for Google Wallet Classes that can be styled.
    """

    # Design Options
    hexBackgroundColor: str | None = None
    logo: Image | None = None
    wideLogo: Image | None = None
    heroImage: Image | None = None


class GoogleWalletStyleableObjectMixin:
    """
    Mixin for Google Wallet Objects that can be styled.

    TODO: Check if really all Objects that can be styled have all four attributes and also with this name.
          Potential Override necessary for programLogo, ...
    """

    # Design Options
    hexBackgroundColor: str | None = None
    logo: Image | None = None
    wideLogo: Image | None = None
    heroImage: Image | None = None
