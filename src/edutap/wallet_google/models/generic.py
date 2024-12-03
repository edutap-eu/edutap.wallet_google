from ..registry import register_model
from .bases import GoogleWalletClassModel
from .bases import GoogleWalletCommonLogosMixin
from .bases import GoogleWalletModel
from .bases import GoogleWalletObjectModel
from .bases import GoogleWalletStyleableMixin
from .primitives import GroupingInfo
from .primitives.enums import GenericType
from .primitives.localized_string import LocalizedString


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
class GenericClass(GoogleWalletClassModel):
    """
    The GenericClass is the implicitly the base class for all other Wallet Class models.
    The Google documentation does not mention this fact.
    This might change in future updates, do not depend on this assumption!

    For now, technically, here are no extra attributes defined!
    In code the GoogleWalletClassModel is the base class.

    see: https://developers.google.com/wallet/generic/rest/v1/genericclass
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-12-02

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
    # inherited appLinkData
    # inherited valueAddedModuleData


@register_model("GenericObject", url_part="genericObject")
class GenericObject(
    GoogleWalletObjectModel,
    GoogleWalletStyleableMixin,
    GoogleWalletCommonLogosMixin,
):
    """
    The GenericObject is a specific object and does not act as the base for other wallet objects!

    see: https://developers.google.com/wallet/generic/rest/v1/genericobject
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    genericType: GenericType = GenericType.GENERIC_TYPE_UNSPECIFIED
    cardTitle: LocalizedString | None = None
    subheader: LocalizedString | None = None
    header: LocalizedString | None = None
    # inherited logo
    # inherited hexBackgroundColor
    notifications: Notifications | None = None
    # inherited id
    # inherited classId
    # inherited barcode
    # inherited heroImage
    # inherited validTimeInterval
    # inherited imageModulesData
    # inherited textModulesData
    # inherited linksModuleData
    # inherited appLinkData
    groupingInfo: GroupingInfo | None = None
    # inherited smartTapRedemptionValue
    # inherited rotatingBarcode
    # inherited state
    # inherited hasUsers
    # inherited messages
    # inherited passConstraints
    # inherited wideLogo
    # inherited saveRestrictions
    # inherited linkedObjectIds
    # inherited valueAddedModuleData
