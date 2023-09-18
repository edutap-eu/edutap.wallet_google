from ..modelbase import GoogleWalletClassModel
from ..modelbase import GoogleWalletObjectModel
from ..registry import register_model
from .primitives import CallbackOptions
from .primitives import GroupingInfo
from .primitives import Image
from .primitives import PassConstraints
from .primitives import SecurityAnimation
from .primitives import Uri
from .primitives.barcode import Barcode
from .primitives.barcode import RotatingBarcode
from .primitives.class_template_info import ClassTemplateInfo
from .primitives.data import AppLinkData
from .primitives.data import ImageModuleData
from .primitives.data import InfoModuleData
from .primitives.data import LinksModuleData
from .primitives.data import TextModuleData
from .primitives.datetime import DateTime
from .primitives.datetime import TimeInterval
from .primitives.enums import MultipleDevicesAndHoldersAllowedStatus
from .primitives.enums import RedemptionChannel
from .primitives.enums import ReviewStatus
from .primitives.enums import State
from .primitives.enums import ViewUnlockRequirement
from .primitives.localized_string import LocalizedString
from .primitives.location import LatLongPoint
from .primitives.money import Money
from .primitives.notification import Message
from .primitives.retail import DiscoverableProgram
from .primitives.review import Review
from pydantic import BaseModel
from pydantic import Field
from pydantic import model_validator


@register_model("giftcardClass", can_disable=False)
class GiftCardClass(GoogleWalletClassModel):
    """
    see: https://developers.google.com/wallet/retail/gift-cards/rest/v1/giftcardclass
    """

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
    classTemplateInfo: ClassTemplateInfo | None = None
    version: str | None = Field(description="deprecated", exclude=True, default=None)
    issuerName: str
    messages: list[Message] | None = None
    allowMultipleUsersPerObject: bool | None = Field(
        description="deprecated", exclude=True, default=None
    )
    homepageUri: Uri | None = None
    locations: list[LatLongPoint]
    reviewStatus: ReviewStatus | None = None
    review: Review | None = None
    infoModuleData: InfoModuleData | None = Field(
        description="deprecated", exclude=True
    )
    imageModulesData: list[ImageModuleData]
    textModulesData: list[TextModuleData] | None = None
    linksModuleData: LinksModuleData | None = None
    redemptionIssuers: list[str] | None = None
    countryCode: str | None = None
    heroImage: Image | None = None
    wordMark: Image | None = Field(description="deprecated", exclude=True)
    enableSmartTap: bool | None = None
    hexBackgroundColor: str | None = None
    localizedIssuerName: LocalizedString | None = None
    multipleDevicesAndHoldersAllowedStatus: MultipleDevicesAndHoldersAllowedStatus | None = (
        MultipleDevicesAndHoldersAllowedStatus.STATUS_UNSPECIFIED
    )
    callbackOptions: CallbackOptions | None = None
    securityAnimation: SecurityAnimation | None = SecurityAnimation
    viewUnlockRequirement: ViewUnlockRequirement = (
        ViewUnlockRequirement.VIEW_UNLOCK_REQUIREMENT_UNSPECIFIED
    )


@register_model("giftcardObject")
class GiftCardObject(GoogleWalletObjectModel):
    """
    see: https://developers.google.com/wallet/retail/gift-cards/rest/v1/giftcardobject
    """

    classReference: GiftCardClass | None = None
    cardNumber: str | None = None
    pin: str | None = None
    balance: Money | None = None
    balanceUpdateTime: DateTime | None = None
    eventNumber: str | None = None
    version: str | None = None
    state: State | None = None
    barcode: Barcode | None = None
    messages: list[Message] | None = None
    validTimeInterval: TimeInterval | None = None
    locations: list[LatLongPoint] | None = None
    hasUsers: bool = False
    smartTapRedemptionValue: str | None = None
    hasLinkedDevice: bool
    disableExpirationNotification: bool
    infoModuleData: InfoModuleData | None = None
    imageModulesData: list[ImageModuleData] | None = None
    textModulesData: list[TextModuleData] | None = None
    linksModuleData: LinksModuleData | None = None
    appLinkData: AppLinkData | None = None
    rotatingBarcode: RotatingBarcode | None = None
    heroImage: Image | None = None
    groupingInfo: GroupingInfo | None = None
    passConstraints: PassConstraints | None = None


@register_model("LoyaltyClass", url_part="loyaltyClass", can_disable=False)
class LoyaltyClass(GoogleWalletClassModel):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyclass
    """

    issuerName: str | None = None
    programName: str | None = None
    programLogo: Image | None = None
    accountNameLabel: str | None = None
    accountIdLabel: str | None = None
    rewardsTierLabel: str | None = None
    rewardsTier: str | None = None
    secondaryRewardsTierLabel: str | None = None
    secondaryRewardsTier: str | None = None
    localizedIssuerName: LocalizedString | None = None
    localizedProgramName: LocalizedString | None = None
    localizedAccountNameLabel: LocalizedString | None = None
    localizedAccountIdLabel: LocalizedString | None = None
    localizedRewardsTierLabel: LocalizedString | None = None
    localizedRewardsTier: LocalizedString | None = None
    localizedSecondaryRewardsTierLabel: LocalizedString | None = None
    localizedSecondaryRewardsTier: LocalizedString | None = None
    discoverableProgram: DiscoverableProgram | None = None
    classTemplateInfo: ClassTemplateInfo | None = None
    version: str | None = Field(
        description="deprecated",
        exclude=True,
        default=None,
    )  # int64
    messages: list[Message] | None = None
    allowMultipleUsersPerObject: bool = Field(
        description="deprecated",
        exclude=True,
        default=True,
    )
    homepageUri: Uri | None = None
    locations: list[LatLongPoint] | None = None
    reviewStatus: ReviewStatus | None = None
    review: Review | None = None
    infoModuleData: InfoModuleData | None = Field(
        description="deprecated",
        exclude=True,
        default=None,
    )
    imageModulesData: list[ImageModuleData] | None = None
    textModulesData: list[TextModuleData] | None = None
    linksModuleData: LinksModuleData | None = None
    redemptionIssuers: list[str] | None = None  # string (int64 format)
    countryCode: str | None = None
    heroImage: Image | None = None
    wordMark: Image | None = Field(
        description="deprecated",
        exclude=True,
        default=None,
    )
    enableSmartTap: bool | None = False
    hexBackgroundColor: str | None = None
    multipleDevicesAndHoldersAllowedStatus: MultipleDevicesAndHoldersAllowedStatus | None = (
        MultipleDevicesAndHoldersAllowedStatus.STATUS_UNSPECIFIED
    )
    callbackOptions: CallbackOptions | None
    securityAnimation: SecurityAnimation | None = SecurityAnimation()
    viewUnlockRequirement: ViewUnlockRequirement | None = (
        ViewUnlockRequirement.VIEW_UNLOCK_REQUIREMENT_UNSPECIFIED
    )


class LoyaltyPointsBalance(BaseModel):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyobject#LoyaltyPointsBalance
    """

    string: str | None = None
    int_: int | None = Field(alias="int", default=None)
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


class LoyaltyPoints(BaseModel):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyobject#LoyaltyPoints
    """

    label: str | None = None
    balance: LoyaltyPointsBalance | None = None
    localizedLabel: LocalizedString | None = None


@register_model("LoyaltyObject", url_part="loyaltyObject")
class LoyaltyObject(GoogleWalletObjectModel):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyobject
    """

    accountName: str | None = None
    accountId: str | None = None
    loyaltyPoints: LoyaltyPoints | None = None
    linkedOfferIds: list[str] | None = None
    secondaryLoyaltyPoints: LoyaltyPoints | None = None
    state: State | None = None
    barcode: Barcode | None = None
    messages: list[Message] | None = None
    validTimeInterval: TimeInterval | None = None
    locations: list[LatLongPoint] | None = None
    hasUsers: bool | None = None
    smartTapRedemptionValue: str | None = None
    hasLinkedDevice: bool | None = None
    disableExpirationNotification: bool | None = None
    imageModule: ImageModuleData | None = None
    imagesModuleData: list[ImageModuleData] | None = None
    textModulesData: list[TextModuleData] | None = None
    appLinkData: AppLinkData | None = None
    rotatingBarcode: RotatingBarcode | None = None
    heroImage: Image | None = None
    groupingInfo: GroupingInfo | None = None
    passConstraints: PassConstraints | None = None


@register_model("OfferClass", url_part="offerClass", can_disable=False)
class OfferClass(GoogleWalletClassModel):
    """
    see: https://developers.google.com/wallet/retail/offers/rest/v1/offerclass
    """

    title: str | None = None
    redemptionChannel: RedemptionChannel | None = None
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
    classTemplateInfo: ClassTemplateInfo | None = None
    version: str | None = None
    issuerName: str | None = None
    messages: list[Message] | None = None
    allowMultipleUsersPerObject: bool = False
    homepageUri: Uri | None = None
    locations: list[LatLongPoint] | None = None
    reviewStatus: ReviewStatus
    review: Review | None = None
    infoModuleData: InfoModuleData | None = None
    imageModulesData: list[ImageModuleData] | None = None
    textModulesData: list[TextModuleData] | None = None
    linksModuleData: LinksModuleData | None = None
    redemptionIssuers: list[str] | None = None
    countryCode: str | None = None
    heroImage: Image | None = None
    wordMark: Image | None = None
    enableSmartTap: bool = False
    hexBackgroundColor: str | None = None
    localizedIssuerName: LocalizedString | None = None
    multipleDevicesAndHoldersAllowedStatus: MultipleDevicesAndHoldersAllowedStatus | None = (
        None
    )
    callbackOptions: CallbackOptions | None = None
    securityAnimation: SecurityAnimation | None = None
    viewUnlockRequirement: ViewUnlockRequirement | None = None


@register_model("OfferObject", url_part="offerObject")
class OfferObject(GoogleWalletObjectModel):
    """
    see: https://developers.google.com/wallet/retail/offers/rest/v1/offerobject
    """

    classReference: OfferClass | None = None
    version: str | None = None
    state: State | None = None
    barcode: Barcode
    messages: list[Message] | None = None
    validTimeInterval: TimeInterval | None = None
    locations: list[LatLongPoint] | None = None
    hasUsers: bool = False
    smartTapRedemptionValue: str
    hasLinkedDevice: bool = False
    disableExpirationNotification: bool = False
    infoModuleData: InfoModuleData | None = None
    imageModulesData: list[ImageModuleData] | None = None
    textModulesData: list[TextModuleData] | None = None
    linksModuleData: LinksModuleData | None = None
    appLinkData: AppLinkData | None = None
    rotatingBarcode: RotatingBarcode | None = None
    heroImage: Image | None = None
    groupingInfo: GroupingInfo | None = None
    passConstraints: PassConstraints | None = None
