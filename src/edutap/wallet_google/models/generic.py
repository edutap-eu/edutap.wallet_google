from ..registry import register_model
from .bases import GoogleWalletClassModel
from .bases import GoogleWalletCommonLogosMixin
from .bases import GoogleWalletMessageableMixin
from .bases import GoogleWalletModel
from .bases import GoogleWalletObjectModel
from .bases import GoogleWalletStyleableMixin
from .primitives import GroupingInfo
from .primitives.data import AppLinkData
from .primitives.datetime import TimeInterval
from .primitives.enums import GenericType
from .primitives.enums import State
from .primitives.localized_string import LocalizedString
from pydantic import Field


class ExpiryNotification(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/genericobject#expirynotification
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    enableNotification: bool = False


class UpcomingNotification(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/genericobject#upcomingnotification
    """

    enableNotification: bool = False


class Notifications(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/genericobject#notifications
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    expiryNotification: ExpiryNotification | None = None
    upcomingNotification: UpcomingNotification | None = None


@register_model(
    "GenericClass", url_part="genericClass", plural="genericClasses", can_disable=False
)
class GenericClass(
    GoogleWalletClassModel,
    GoogleWalletMessageableMixin,
):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/genericclass
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    # inherited id
    # inherited classTemplateInfo
    # inherited infoModuleData
    # inherited imageModulesData
    # inherited textModulesData
    # inherited linksModuleData
    # inherited enableSmartTap
    # inherited redemptionIssuers
    # inherited securityAnimation
    # inherited multipleDevicesAndHoldersAllowedStatus
    # inherited callbackOptions
    # inherited viewUnlockRequirement
    # inherited messages
    # TODO appLinkData
    # TODO valueAddedModuleData


@register_model("GenericObject", url_part="genericObject")
class GenericObject(
    GoogleWalletObjectModel,
    GoogleWalletStyleableMixin,
    GoogleWalletCommonLogosMixin,
    GoogleWalletMessageableMixin,
):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/genericobject
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    genericType: GenericType = GenericType.GENERIC_TYPE_UNSPECIFIED
    cardTitle: LocalizedString | None = None
    subheader: LocalizedString | None = None
    header: LocalizedString | None = None
    # inherited logo
    # inhertied hexBackgroundColor
    notifications: Notifications | None = None
    # inherited id
    # inherited classId
    # inherited barcode
    # inherited heroImage
    validTimeInterval: TimeInterval | None = None
    # inherited imageModulesData
    # inherited textModulesData
    # inherited linksModuleData
    appLinkData: AppLinkData | None = None
    groupingInfo: GroupingInfo | None = None
    # inherited smartTapRedemptionValue
    # inherited rotatingBarcode
    state: State = Field(default=State.STATE_UNSPECIFIED)
    hasUsers: bool | None = None
    # inherited messages
    # inherited passConstraints
    # inherited wideLogo
    # TODO saveRestrictions
    # TODO linkedObjectIds
    # TODO valueAddedModuleData
