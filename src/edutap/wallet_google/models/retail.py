from ..registry import register_model
from .bases import GoogleWalletClassModel
from .bases import GoogleWalletModel
from .bases import GoogleWalletObjectModel
from .bases import GoogleWalletObjectWithClassReferenceMixin
from .bases import GoogleWalletStyleableMixin
from .primitives import GroupingInfo
from .primitives import Image
from .primitives import PassConstraints
from .primitives import Uri
from .primitives.data import ImageModuleData
from .primitives.datetime import DateTime
from .primitives.enums import NotificationSettingsForUpdates
from .primitives.enums import RedemptionChannel
from .primitives.enums import ReviewStatus
from .primitives.localized_string import LocalizedString
from .primitives.location import LatLongPoint
from .primitives.money import Money
from .primitives.retail import DiscoverableProgram
from .primitives.review import Review
from pydantic import Field
from pydantic import model_validator


@register_model(
    "GiftCardClass",
    url_part="giftCardClass",
    plural="giftCardClasses",
    can_disable=False,
)
class GiftCardClass(
    GoogleWalletClassModel,
    GoogleWalletStyleableMixin,
):
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
    # inherited classTemplateInfo
    # inherited id
    version: str | None = Field(description="deprecated", exclude=True, default=None)
    issuerName: str
    # inherited messages
    homepageUri: Uri | None = None
    reviewStatus: ReviewStatus = ReviewStatus.REVIEW_STATUS_UNSPECIFIED
    review: Review | None = None
    # inherited imageModulesData
    # inherited textModulesData
    # inherited linksModuleData
    # inherited redemptionIssuers
    countryCode: str | None = None
    heroImage: Image | None = None
    # inherited enableSmartTap
    # inherited hexBackgroundColor
    localizedIssuerName: LocalizedString | None = None
    # inherited multipleDevicesAndHoldersAllowedStatus
    # inherited callbackOptions
    # inherited securityAnimation
    # inherited viewUnlockRequirement
    wideProgramLogo: Image | None = None
    notifyPreference: NotificationSettingsForUpdates = (
        NotificationSettingsForUpdates.NOTIFICATION_SETTINGS_FOR_UPDATES_UNSPECIFIED
    )
    # inherited appLinkData
    # inherited valueAddedModuleData


@register_model("GiftCardObject", url_part="giftCardObject")
class GiftCardObject(
    GoogleWalletObjectModel,
    GoogleWalletObjectWithClassReferenceMixin,
):
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
    # inherited id
    # inherited version
    # inherited state
    # inherited barcode
    # inherited messages
    # inherited validTimeInterval
    locations: list[LatLongPoint] | None = None
    # inherited hasUsers
    # inherited smartTapRedemptionValue
    hasLinkedDevice: bool = False
    disableExpirationNotification: bool | None = False
    # inherited infoModuleData
    # inherited imageModulesData
    # inherited textModulesData
    # inherited linksModuleData
    # inherited appLinkData
    # inherited rotatingBarcode
    heroImage: Image | None = None
    # inherited groupingInfo
    # inherited passConstraints
    # inherited saveRestrictions
    # inherited linkedObjectIds
    notifyPreference: NotificationSettingsForUpdates = (
        NotificationSettingsForUpdates.NOTIFICATION_SETTINGS_FOR_UPDATES_UNSPECIFIED
    )
    # inherited valueAddedModuleData


@register_model(
    "LoyaltyClass", url_part="loyaltyClass", plural="loyaltyClasses", can_disable=False
)
class LoyaltyClass(
    GoogleWalletClassModel,
    GoogleWalletStyleableMixin,
):
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
    # inherited classTemplateInfo
    # inherited id
    issuerName: str | None = None
    # inherited messages
    homepageUri: Uri | None = None
    locations: list[LatLongPoint] | None = None
    review: Review | None = None
    reviewStatus: ReviewStatus = ReviewStatus.REVIEW_STATUS_UNSPECIFIED
    # inherited infoModuleData
    # inherited imageModulesData
    # inherited textModulesData
    # inherited linksModuleData
    # inherited redemptionIssuers
    countryCode: str | None = None
    heroImage: Image | None = None
    # inherited wordMark
    # inherited enableSmartTap
    # inherited hexBackgroundColor
    localizedIssuerName: LocalizedString | None = None
    # inherited multipleDevicesAndHoldersAllowedStatus
    # inherited callbackOptions
    # inherited securityAnimation
    # inherited viewUnlockRequirement
    wideProgramLogo: Image | None = None
    notifyPreference: NotificationSettingsForUpdates = (
        NotificationSettingsForUpdates.NOTIFICATION_SETTINGS_FOR_UPDATES_UNSPECIFIED
    )
    # inherited valueAddedModuleData


class LoyaltyPointsBalance(
    GoogleWalletModel,
):
    """
    data-type,
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyobject#LoyaltyPointsBalance
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # Most deprecated are skipped.
    # last check: 2024-11-29

    string: str | None = None
    int_: int | None = Field(alias="int", serialization_alias="int", default=None)
    double: float | None = None
    money: Money | None = None

    @model_validator(mode="after")
    def check_one_of(self) -> "LoyaltyPointsBalance":
        given_values = [
            val
            for val in (self.string, self.int_, self.double, self.money)
            if val is not None
        ]
        if len(given_values) == 0:
            raise ValueError("One of string, int, double, or money must be set")
        if len(given_values) > 1:
            raise ValueError("Only one of string, int, double, or money must be set")
        return self


class LoyaltyPoints(
    GoogleWalletModel,
):
    """
    data-type,
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyobject#LoyaltyPoints
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # Most deprecated are skipped.
    # last check: 2024-11-29

    label: str | None = None
    balance: LoyaltyPointsBalance | None = None
    localizedLabel: LocalizedString | None = None


@register_model("LoyaltyObject", url_part="loyaltyObject", plural="loyaltyObjects")
class LoyaltyObject(
    GoogleWalletObjectModel,
    GoogleWalletObjectWithClassReferenceMixin,
):
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
    # inherited id
    # inherited classId
    # inherited messages
    # inherited state
    # inherited barcode
    # inherited messages
    # inherited validTimeInterval
    # inherited hasUsers
    # inherited smartTapRedemptionValue
    hasLinkedDevice: bool | None = None
    disableExpirationNotification: bool | None = False
    imageModule: ImageModuleData | None = None
    # inherited infoModuleData
    # inherited imageModulesData
    # inherited textModulesData
    # inherited linksModuleData
    # inherited appLinkData
    # inherited rotatingBarcode
    heroImage: Image | None = None
    # inherited groupingInfo
    # inhertied passConstraints
    # inherited saveRestrictions
    # inherited linkedObjectIds
    notifyPreference: NotificationSettingsForUpdates = (
        NotificationSettingsForUpdates.NOTIFICATION_SETTINGS_FOR_UPDATES_UNSPECIFIED
    )
    # inherited valueAddedModuleData


@register_model(
    "OfferClass", url_part="offerClass", plural="offerClasses", can_disable=False
)
class OfferClass(
    GoogleWalletClassModel,
    GoogleWalletStyleableMixin,
):
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
    # inherited classTemplateInfo
    # inherited id
    issuerName: str | None = None
    # inherited messages
    homepageUri: Uri | None = None
    reviewStatus: ReviewStatus = ReviewStatus.REVIEW_STATUS_UNSPECIFIED
    review: Review | None = None
    # inherited infoModuleData
    # inherited imageModulesData
    # inherited textModulesData
    # inherited linksModuleData
    # inherited redemptionIssuers
    countryCode: str | None = None
    heroImage: Image | None = None
    # inherited enableSmartTap
    # inherited hexBackgroundColor
    localizedIssuerName: LocalizedString | None = None
    # inherited multipleDevicesAndHoldersAllowedStatus
    # inherited callbackOptions
    # inherited securityAnimation
    # inherited viewUnlockRequirement
    wideTitleImage: Image | None = None
    notifyPreference: NotificationSettingsForUpdates = (
        NotificationSettingsForUpdates.NOTIFICATION_SETTINGS_FOR_UPDATES_UNSPECIFIED
    )
    # inherited appLinkData
    # inherited valueAddedModuleData


@register_model("OfferObject", url_part="offerObject")
class OfferObject(
    GoogleWalletObjectModel,
    GoogleWalletObjectWithClassReferenceMixin,
    GoogleWalletStyleableMixin,
):
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
    # inherited id
    # inherited classId
    # inherited state
    # inherited barcode
    # inertied messages
    # inherited validTimeInterval
    locations: list[LatLongPoint] | None = None
    # inherited hasUsers
    # inherited smartTapRedemptionValue
    hasLinkedDevice: bool = False
    disableExpirationNotification: bool | None = False
    # inherited infoModuleData
    # inherited imageModulesData
    # inherited textModulesData
    # inherited linksModuleData
    # inherited appLinkData
    # inherited rotatingBarcode
    heroImage: Image | None = None
    groupingInfo: GroupingInfo | None = None
    passConstraints: PassConstraints | None = None
    # inherited saveRestrictions
    # inherited linkedObjectIds
    notifyPreference: NotificationSettingsForUpdates = (
        NotificationSettingsForUpdates.NOTIFICATION_SETTINGS_FOR_UPDATES_UNSPECIFIED
    )
    # inherited valueAddedModuleData
