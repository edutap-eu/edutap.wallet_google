from ...registry import register_model
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
from ..deprecated import DeprecatedAllowMultipleUsersPerObjectMixin
from ..deprecated import DeprecatedInfoModuleDataFieldMixin
from ..deprecated import DeprecatedKindFieldMixin
from ..deprecated import DeprecatedLocationsFieldMixin
from ..deprecated import DeprecatedVersionFieldMixin
from ..deprecated import DeprecatedWordMarkFieldMixin
from .bases import ClassModel
from .bases import ObjectModel
from .bases import StyleableMixin


# Attribute order as in Google's documentation to make future updates easier!
# last check: 2025-01-22


@register_model("GiftCardClass", url_part="giftCardClass", plural="giftCardClasses")
class GiftCardClass(
    DeprecatedKindFieldMixin,
    DeprecatedVersionFieldMixin,
    DeprecatedAllowMultipleUsersPerObjectMixin,
    DeprecatedLocationsFieldMixin,
    DeprecatedInfoModuleDataFieldMixin,
    DeprecatedWordMarkFieldMixin,
    StyleableMixin,
    ClassModel,
):
    """
    see: https://developers.google.com/wallet/retail/gift-cards/rest/v1/giftcardclass
    """

    # inherits kind (deprecated)
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
    # inherits version (deprecated)
    issuerName: str
    # inherits messages
    # inherits allowMultipleUsersPerObject (deprecated)
    homepageUri: Uri | None = None
    # inherits locations (deprecated)
    reviewStatus: ReviewStatus = ReviewStatus.REVIEW_STATUS_UNSPECIFIED
    review: Review | None = None
    # inherits infoModuleData (deprecated)
    # inherits imageModulesData
    # inherits textModulesData
    # inherits linksModuleData
    # inherits redemptionIssuers
    countryCode: str | None = None
    heroImage: Image | None = None
    # inherits wordMark (deprecated)
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
class GiftCardObject(
    DeprecatedKindFieldMixin,
    DeprecatedVersionFieldMixin,
    DeprecatedLocationsFieldMixin,
    ObjectModel,
):
    """
    see: https://developers.google.com/wallet/retail/gift-cards/rest/v1/giftcardobject
    """

    # inherits kind (deprecated)
    classReference: GiftCardClass | None = None
    cardNumber: str | None = None
    pin: str | None = None
    balance: Money | None = None
    balanceUpdateTime: DateTime | None = None
    eventNumber: str | None = None
    # inherits id
    # inherits classId
    # inherits version (deprecated)
    # inherits state
    # inherits barcode
    # inherits messages
    # inherits validTimeInterval
    # inherits locations (deprecated)
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


@register_model("LoyaltyClass", url_part="loyaltyClass", plural="loyaltyClasses")
class LoyaltyClass(
    DeprecatedKindFieldMixin,
    DeprecatedVersionFieldMixin,
    DeprecatedAllowMultipleUsersPerObjectMixin,
    DeprecatedInfoModuleDataFieldMixin,
    DeprecatedWordMarkFieldMixin,
    StyleableMixin,
    ClassModel,
):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyclass
    """

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
    # inherits version (deprecated)
    issuerName: str | None = None
    # inherits messages
    # inherits allowMultipleUsersPerObject (deprecated)
    homepageUri: Uri | None = None
    locations: list[LatLongPoint] | None = None
    reviewStatus: ReviewStatus = ReviewStatus.REVIEW_STATUS_UNSPECIFIED
    review: Review | None = None
    # inherits infoModuleData (deprecated)
    # inherits imageModulesData
    # inherits textModulesData
    # inherits linksModuleData
    # inherits redemptionIssuers
    countryCode: str | None = None
    heroImage: Image | None = None
    # inherits wordMark (deprecated)
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


@register_model("LoyaltyObject", url_part="loyaltyObject", plural="loyaltyObjects")
class LoyaltyObject(
    DeprecatedKindFieldMixin,
    DeprecatedVersionFieldMixin,
    DeprecatedLocationsFieldMixin,
    ObjectModel,
):
    """
    data-type,
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyobject
    """

    # inherits kind (deprecated)
    classReference: LoyaltyClass | None = None
    accountName: str | None = None
    accountId: str | None = None
    loyaltyPoints: LoyaltyPoints | None = None
    linkedOfferIds: list[str] | None = None
    secondaryLoyaltyPoints: LoyaltyPoints | None = None
    # inherits id
    # inherits classId
    # inherits messages
    # inherits version (deprecated)
    # inherits state
    # inherits barcode
    # inherits messages
    # inherits validTimeInterval
    # inherits locations (deprecated)
    # inherits hasUsers
    # inherits smartTapRedemptionValue
    hasLinkedDevice: bool | None = None
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


@register_model("OfferClass", url_part="offerClass", plural="offerClasses")
class OfferClass(
    DeprecatedKindFieldMixin,
    DeprecatedVersionFieldMixin,
    DeprecatedAllowMultipleUsersPerObjectMixin,
    DeprecatedLocationsFieldMixin,
    DeprecatedInfoModuleDataFieldMixin,
    DeprecatedWordMarkFieldMixin,
    StyleableMixin,
    ClassModel,
):
    """
    see: https://developers.google.com/wallet/retail/offers/rest/v1/offerclass
    """

    # inherits kind (deprecated)
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
    # inherits version (deprecated)
    issuerName: str | None = None
    # inherits messages
    # inherits allowMultipleUsersPerObject (deprecated)
    homepageUri: Uri | None = None
    # inherits locations (deprecated)
    reviewStatus: ReviewStatus = ReviewStatus.REVIEW_STATUS_UNSPECIFIED
    review: Review | None = None
    # inherits infoModuleData (deprecated)
    # inherits imageModulesData
    # inherits textModulesData
    # inherits linksModuleData
    # inherits redemptionIssuers
    countryCode: str | None = None
    heroImage: Image | None = None
    # inherits wordMark (deprecated)
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
class OfferObject(
    DeprecatedKindFieldMixin,
    DeprecatedVersionFieldMixin,
    StyleableMixin,
    ObjectModel,
):
    """
    see: https://developers.google.com/wallet/retail/offers/rest/v1/offerobject
    """

    # inherits kind (deprecated)
    classReference: OfferClass | None = None
    # inherits id
    # inherits classId
    # inherits version (deprecated)
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
    groupingInfo: GroupingInfo | None = None
    passConstraints: PassConstraints | None = None
    # inherits saveRestrictions
    # inherits linkedObjectIds
    notifyPreference: NotificationSettingsForUpdates = (
        NotificationSettingsForUpdates.NOTIFICATION_SETTINGS_FOR_UPDATES_UNSPECIFIED
    )
    # inherits valueAddedModuleData
