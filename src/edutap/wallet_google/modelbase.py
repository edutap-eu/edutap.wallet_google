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
from .models.primitives.enums import ViewUnlockRequirement
from .models.primitives.notification import Message
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class GoogleWalletModel(BaseModel):
    """
    Base model for all Google Wallet models.
    """

    model_config = ConfigDict(
        extra="forbid",
        # extra="ignore",
        use_enum_values=True,
    )


class GoogleWalletWithIdModel(GoogleWalletModel):
    """
    Base model for Google Wallet models with an identifier.
    """

    kind: str | None = Field(description="deprecated", exclude=True, default=None)
    id: str


class GoogleWalletClassModel(GoogleWalletWithIdModel):
    """
    Base model for all Google Wallet Class models.
    """

    classTemplateInfo: ClassTemplateInfo | None = None
    imageModulesData: list[ImageModuleData] | None = None
    textModulesData: list[TextModuleData] | None = None
    linksModuleData: LinksModuleData | None = None
    infoModuleData: InfoModuleData | None = Field(
        description="deprecated", exclude=True, default=None
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

    # Design Options
    hexBackgroundColor: str | None = None
    logo: Image | None = None
    wideLogo: Image | None = None
    heroImage: Image | None = None
    wordMark: Image | None = Field(description="deprecated", exclude=True, default=None)


class GoogleWalletObjectModel(GoogleWalletWithIdModel):
    """
    Base model for all Google Wallet Object models.
    """

    classId: str

    groupingInfo: GroupingInfo | None = None

    # Security Options
    passConstraints: PassConstraints | None = None

    # Barcode Options
    barcode: Barcode | None = None
    rotatingBarcode: RotatingBarcode | None = None


class GoogleWalletObjectReference(GoogleWalletObjectModel):
    """
    Model for all Google Wallet Object with a Class references.
    """

    classReference: GoogleWalletClassModel | None = None


class GoogleWalletMessageble(GoogleWalletWithIdModel):
    """
    Model for Google Wallet Classes or Objects that can retrieve Messages
    """

    messages: list[Message] | None = None
