from ...registry import register_model
from ..datatypes.data import ImageModuleData
from ..datatypes.datetime import DateTime
from ..datatypes.enums import NotificationSettingsForUpdates
from ..datatypes.enums import RedemptionChannel
from ..datatypes.enums import ReviewStatus
from ..datatypes.general import GroupingInfo
from ..datatypes.general import Image
from ..datatypes.general import PassConstraints
from ..datatypes.general import Uri
from ..datatypes.localized_string import LocalizedString
from ..datatypes.location import LatLongPoint
from ..datatypes.loyalty import LoyaltyPoints
from ..datatypes.money import Money
from ..datatypes.retail import DiscoverableProgram
from ..datatypes.review import Review
from .bases import ClassModel
from .bases import ObjectModel
from .bases import StyleableMixin
from pydantic import Field


@register_model(
    "GiftCardClass",
    url_part="giftCardClass",
    plural="giftCardClasses",
    can_disable=False,
)
class GiftCardClass(ClassModel, StyleableMixin):
    """
    see: https://developers.google.com/wallet/retail/gift-cards/rest/v1/giftcardclass
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # Most deprecated are skipped.
    # last check: 2024-11-29

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default="walletobjects#giftCardClass",
    )
    merchantName: str | None = None
    programLogo: Image | None = None
    pinLabel: str | None = None
    eventNumberLabel: str | None = None
    allowBarcodeRedemption: bool = False
    localizedMerchantName: LocalizedString | None = None
    localizedPinLabel: LocalizedString | None = None
    localizedEventNumberLabel: LocalizedString | None = None
    cardNumberLabel: str | None = None
    localizedCardNumberLabel: LocalizedString | None = None
    # inherits classTemplateInfo
    # inherits id
    version: str | None = Field(description="deprecated", exclude=True, default=None)
    issuerName: str
    # inherits messages
    homepageUri: Uri | None = None
    reviewStatus: ReviewStatus = ReviewStatus.REVIEW_STATUS_UNSPECIFIED
    review: Review | None = None
    # inherits imageModulesData
    # inherits textModulesData
    # inherits linksModuleData
    # inherits redemptionIssuers
    countryCode: str | None = None
    heroImage: Image | None = None
    # inherits enableSmartTap
    # inherits hexBackgroundColor
    localizedIssuerName: LocalizedString | None = None
    # inherits multipleDevicesAndHoldersAllowedStatus
    # inherits callbackOptions
    # inherits securityAnimation
    # inherits viewUnlockRequirement
    wideProgramLogo: Image | None = None
    notifyPreference: NotificationSettingsForUpdates = (
        NotificationSettingsForUpdates.NOTIFICATION_SETTINGS_FOR_UPDATES_UNSPECIFIED
    )
    # inherits appLinkData
    # inherits valueAddedModuleData


@register_model("GiftCardObject", url_part="giftCardObject")
class GiftCardObject(ObjectModel):
    """
    see: https://developers.google.com/wallet/retail/gift-cards/rest/v1/giftcardobject
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # Most deprecated are skipped.
    # last check: 2024-11-29

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default="walletobjects#giftCardObject",
    )

    classReference: GiftCardClass | None = None
    cardNumber: str | None = None
    pin: str | None = None
    balance: Money | None = None
    balanceUpdateTime: DateTime | None = None
    eventNumber: str | None = None
    # inherits id
    # inherits version
    # inherits state
    # inherits barcode
    # inherits messages
    # inherits validTimeInterval
    locations: list[LatLongPoint] | None = None
    # inherits hasUsers
    # inherits smartTapRedemptionValue
    hasLinkedDevice: bool = False
    disableExpirationNotification: bool | None = False
    # inherits infoModuleData
    # inherits imageModulesData
    # inherits textModulesData
    # inherits linksModuleData
    # inherits appLinkData
    # inherits rotatingBarcode
    heroImage: Image | None = None
    # inherits groupingInfo
    # inherits passConstraints
    # inherits saveRestrictions
    # inherits linkedObjectIds
    notifyPreference: NotificationSettingsForUpdates = (
        NotificationSettingsForUpdates.NOTIFICATION_SETTINGS_FOR_UPDATES_UNSPECIFIED
    )
    # inherits valueAddedModuleData


@register_model(
    "LoyaltyClass", url_part="loyaltyClass", plural="loyaltyClasses", can_disable=False
)
class LoyaltyClass(ClassModel, StyleableMixin):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyclass
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # Most deprecated are skipped.
    # last check: 2024-11-29

    # deprecated
    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default="walletobjects#loyaltyClass",
    )

    programName: str | None = None
    programLogo: Image | None = None
    accountNameLabel: str | None = None
    accountIdLabel: str | None = None
    rewardsTierLabel: str | None = None
    rewardsTier: str | None = None
    localizedProgramName: LocalizedString | None = None
    localizedAccountNameLabel: LocalizedString | None = None
    localizedAccountIdLabel: LocalizedString | None = None
    localizedRewardsTierLabel: LocalizedString | None = None
    localizedRewardsTier: LocalizedString | None = None
    secondaryRewardsTierLabel: str | None = None
    localizedSecondaryRewardsTierLabel: LocalizedString | None = None
    secondaryRewardsTier: str | None = None
    localizedSecondaryRewardsTier: LocalizedString | None = None
    discoverableProgram: DiscoverableProgram | None = None
    # inherits classTemplateInfo
    # inherits id
    issuerName: str | None = None
    # inherits messages
    homepageUri: Uri | None = None
    locations: list[LatLongPoint] | None = None
    review: Review | None = None
    reviewStatus: ReviewStatus = ReviewStatus.REVIEW_STATUS_UNSPECIFIED
    # inherits infoModuleData
    # inherits imageModulesData
    # inherits textModulesData
    # inherits linksModuleData
    # inherits redemptionIssuers
    countryCode: str | None = None
    heroImage: Image | None = None
    # inherits wordMark
    # inherits enableSmartTap
    # inherits hexBackgroundColor
    localizedIssuerName: LocalizedString | None = None
    # inherits multipleDevicesAndHoldersAllowedStatus
    # inherits callbackOptions
    # inherits securityAnimation
    # inherits viewUnlockRequirement
    wideProgramLogo: Image | None = None
    notifyPreference: NotificationSettingsForUpdates = (
        NotificationSettingsForUpdates.NOTIFICATION_SETTINGS_FOR_UPDATES_UNSPECIFIED
    )
    # inherits valueAddedModuleData


@register_model("LoyaltyObject", url_part="loyaltyObject", plural="loyaltyObjects")
class LoyaltyObject(ObjectModel):
    """
    data-type,
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyobject
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # Most deprecated are skipped.
    # last check: 2024-11-29

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default="walletobjects#loyaltyObject",
    )

    classReference: LoyaltyClass | None = None
    accountName: str | None = None
    accountId: str | None = None
    loyaltyPoints: LoyaltyPoints | None = None
    linkedOfferIds: list[str] | None = None
    secondaryLoyaltyPoints: LoyaltyPoints | None = None
    # inherits id
    # inherits classId
    # inherits messages
    # inherits state
    # inherits barcode
    # inherits messages
    # inherits validTimeInterval
    # inherits hasUsers
    # inherits smartTapRedemptionValue
    hasLinkedDevice: bool | None = None
    disableExpirationNotification: bool | None = False
    imageModule: ImageModuleData | None = None
    # inherits infoModuleData
    # inherits imageModulesData
    # inherits textModulesData
    # inherits linksModuleData
    # inherits appLinkData
    # inherits rotatingBarcode
    heroImage: Image | None = None
    # inherits groupingInfo
    # inherits passConstraints
    # inherits saveRestrictions
    # inherits linkedObjectIds
    notifyPreference: NotificationSettingsForUpdates = (
        NotificationSettingsForUpdates.NOTIFICATION_SETTINGS_FOR_UPDATES_UNSPECIFIED
    )
    # inherits valueAddedModuleData


@register_model(
    "OfferClass", url_part="offerClass", plural="offerClasses", can_disable=False
)
class OfferClass(ClassModel, StyleableMixin):
    """
    see: https://developers.google.com/wallet/retail/offers/rest/v1/offerclass
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # Most deprecated are skipped.
    # last check: 2024-11-29

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default="walletobjects#offerClass",
    )

    title: str | None = None
    redemptionChannel: RedemptionChannel = (
        RedemptionChannel.REDEMPTION_CHANNEL_UNSPECIFIED
    )
    provider: str | None = None
    titleImage: Image | None = None
    details: str | None = None
    finePrint: str | None = None
    helpUri: Uri | None = None
    localizedTitle: LocalizedString | None = None
    localizedProvider: LocalizedString | None = None
    localizedDetails: LocalizedString | None = None
    localizedFinePrint: LocalizedString | None = None
    shortTitle: str | None = None
    localizedShortTitle: LocalizedString | None = None
    # inherits classTemplateInfo
    # inherits id
    issuerName: str | None = None
    # inherits messages
    homepageUri: Uri | None = None
    reviewStatus: ReviewStatus = ReviewStatus.REVIEW_STATUS_UNSPECIFIED
    review: Review | None = None
    # inherits infoModuleData
    # inherits imageModulesData
    # inherits textModulesData
    # inherits linksModuleData
    # inherits redemptionIssuers
    countryCode: str | None = None
    heroImage: Image | None = None
    # inherits enableSmartTap
    # inherits hexBackgroundColor
    localizedIssuerName: LocalizedString | None = None
    # inherits multipleDevicesAndHoldersAllowedStatus
    # inherits callbackOptions
    # inherits securityAnimation
    # inherits viewUnlockRequirement
    wideTitleImage: Image | None = None
    notifyPreference: NotificationSettingsForUpdates = (
        NotificationSettingsForUpdates.NOTIFICATION_SETTINGS_FOR_UPDATES_UNSPECIFIED
    )
    # inherits appLinkData
    # inherits valueAddedModuleData


@register_model("OfferObject", url_part="offerObject")
class OfferObject(ObjectModel, StyleableMixin):
    """
    see: https://developers.google.com/wallet/retail/offers/rest/v1/offerobject
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # Most deprecated are skipped.
    # last check: 2024-11-29

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default="walletobjects#offerClass",
    )

    classReference: OfferClass | None = None
    # inherits id
    # inherits classId
    # inherits state
    # inherits barcode
    # inertied messages
    # inherits validTimeInterval
    locations: list[LatLongPoint] | None = None
    # inherits hasUsers
    # inherits smartTapRedemptionValue
    hasLinkedDevice: bool = False
    disableExpirationNotification: bool | None = False
    # inherits infoModuleData
    # inherits imageModulesData
    # inherits textModulesData
    # inherits linksModuleData
    # inherits appLinkData
    # inherits rotatingBarcode
    heroImage: Image | None = None
    groupingInfo: GroupingInfo | None = None
    passConstraints: PassConstraints | None = None
    # inherits saveRestrictions
    # inherits linkedObjectIds
    notifyPreference: NotificationSettingsForUpdates = (
        NotificationSettingsForUpdates.NOTIFICATION_SETTINGS_FOR_UPDATES_UNSPECIFIED
    )
    # inherits valueAddedModuleData
