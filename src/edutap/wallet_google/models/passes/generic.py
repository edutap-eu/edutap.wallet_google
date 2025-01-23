from ...registry import register_model
from ..datatypes.enums import GenericType
from ..datatypes.general import GroupingInfo
from ..datatypes.localized_string import LocalizedString
from ..datatypes.notification import Notifications
from .bases import ClassModel
from .bases import CommonLogosMixin
from .bases import ObjectModel
from .bases import StyleableMixin


# Attribute order as in Google's documentation to make future updates easier!
# last check: 2025-01-22


@register_model(
    "GenericClass",
    url_part="genericClass",
    plural="genericClasses",
    can_message=True,
)
class GenericClass(ClassModel):
    """
    The GenericClass is the implicitly the base class for all other Wallet Class models.
    The Google documentation does not mention this fact.
    This might change in future updates, do not depend on this assumption!

    For now, technically, here are no extra attributes defined!
    In code the ClassModel is the base class.

    see: https://developers.google.com/wallet/generic/rest/v1/genericclass
    """

    # inherits id
    # inherits classTemplateInfo
    # inherits infoModuleData
    # inherits imageModulesData
    # inherits textModulesData
    # inherits linksModuleData
    # inherits enableSmartTap
    # inherits redemptionIssuers
    # inherits securityAnimation
    # inherits multipleDevicesAndHoldersAllowedStatus
    # inherits callbackOptions
    # inherits viewUnlockRequirement
    # inherits messages
    # inherits appLinkData
    # inherits valueAddedModuleData


@register_model("GenericObject", url_part="genericObject", can_message=True)
class GenericObject(StyleableMixin, CommonLogosMixin, ObjectModel):
    """
    The GenericObject is a specific object and does not act as the base for other wallet objects!

    see: https://developers.google.com/wallet/generic/rest/v1/genericobject
    """

    genericType: GenericType = GenericType.GENERIC_TYPE_UNSPECIFIED
    cardTitle: LocalizedString | None = None
    subheader: LocalizedString | None = None
    header: LocalizedString | None = None
    # inherits logo
    # inherits hexBackgroundColor
    notifications: Notifications | None = None
    # inherits id
    # inherits classId
    # inherits barcode
    # inherits heroImage
    # inherits validTimeInterval
    # inherits imageModulesData
    # inherits textModulesData
    # inherits linksModuleData
    # inherits appLinkData
    groupingInfo: GroupingInfo | None = None
    # inherits smartTapRedemptionValue
    # inherits rotatingBarcode
    # inherits state
    # inherits hasUsers
    # inherits messages
    # inherits passConstraints
    # inherits wideLogo
    # inherits saveRestrictions
    # inherits valueAddedModuleData
    # inherits linkedObjectIds
