from ..registry import register_model
from ..registry import RegistrationType
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


# @register_model(RegistrationType.WALLETCLASS, "giftcard")
@register_model("gitCardClass")
class GiftCardClass(BaseModel):
    """
    see: https://developers.google.com/wallet/retail/gift-cards/rest/v1/giftcardclass
    """

    id: str
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


# @register_model(RegistrationType.WALLETOBJECT, "giftcard")
@register_model("giftcardObject")
class GiftCardObject(BaseModel):
    """
    see: https://developers.google.com/wallet/retail/gift-cards/rest/v1/giftcardobject
    """

    id: str
    classReference: GiftCardClass | None
    cardNumber: str | None
    pin: str | None
    balance: Money | None
    balanceUpdateTime: DateTime | None
    eventNumber: str | None
    classId: str | None
    version: str | None
    state: State | None
    barcode: Barcode | None
    messages: list[Message] | None
    validTimeInterval: TimeInterval | None
    locations: list[LatLongPoint] | None
    hasUsers: bool = False
    smartTapRedemptionValue: str | None
    hasLinkedDevice: bool
    disableExpirationNotification: bool
    infoModuleData: InfoModuleData | None
    imageModulesData: list[ImageModuleData] | None
    textModulesData: list[TextModuleData] | None
    linksModuleData: LinksModuleData | None
    appLinkData: AppLinkData | None
    rotatingBarcode: RotatingBarcode | None
    heroImage: Image | None
    groupingInfo: GroupingInfo | None
    passConstraints: PassConstraints | None


# @register_model(RegistrationType.WALLETCLASS, "loyalty")
@register_model("loyaltyClass", has_addmessage=True)
class LoyaltyClass(BaseModel):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyclass
    """

    id: str
    issuerName: str | None
    programName: str | None
    programLogo: Image | None
    accountNameLabel: str | None
    accountIdLabel: str | None
    rewardsTierLabel: str | None
    rewardsTier: str | None
    secondaryRewardsTierLabel: str | None
    secondaryRewardsTier: str | None
    localizedIssuerName: LocalizedString | None
    localizedProgramName: LocalizedString | None
    localizedAccountNameLabel: LocalizedString | None
    localizedAccountIdLabel: LocalizedString | None
    localizedRewardsTierLabel: LocalizedString | None
    localizedRewardsTier: LocalizedString | None
    localizedSecondaryRewardsTierLabel: LocalizedString | None
    localizedSecondaryRewardsTier: LocalizedString | None
    discoverableProgram: DiscoverableProgram | None
    classTemplateInfo: ClassTemplateInfo | None
    version: str | None = Field(description="deprecated", exclude=True)  # int64
    messages: list[Message] | None
    allowMultipleUsersPerObject: bool = Field(
        description="deprecated", exclude=True, default=True
    )
    homepageUri: Uri | None
    locations: list[LatLongPoint] | None
    reviewStatus: ReviewStatus | None
    review: Review | None
    infoModuleData: InfoModuleData | None = Field(
        description="deprecated", exclude=True
    )
    imageModulesData: list[ImageModuleData] | None
    textModulesData: list[TextModuleData] | None
    linksModuleData: LinksModuleData | None
    redemptionIssuers: list[str] | None  # string (int64 format)
    countryCode: str | None
    heroImage: Image | None
    wordMark: Image | None = Field(description="deprecated", exclude=True)
    enableSmartTap: bool | None = False
    hexBackgroundColor: str | None
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

    label: str | None
    balance: LoyaltyPointsBalance | None
    localizedLabel: LocalizedString | None


# @register_model(RegistrationType.WALLETOBJECT, "loyalty")
@register_model("loyaltyObject", has_addmessage=True)
class LoyaltyObject(BaseModel):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyobject
    """

    id: str
    classId: str
    accountName: str | None
    accountId: str | None
    loyaltyPoints: LoyaltyPoints | None
    linkedOfferIds: list[str] | None
    secondaryLoyaltyPoints: LoyaltyPoints | None
    state: State | None
    barcode: Barcode | None
    messages: list[Message] | None
    validTimeInterval: TimeInterval | None
    locations: list[LatLongPoint] | None
    hasUsers: bool | None
    smartTapRedemptionValue: str | None
    hasLinkedDevice: bool | None
    disableExpirationNotification: bool | None
    imageModule: ImageModuleData | None
    imagesModuleData: list[ImageModuleData] | None
    textModulesData: list[TextModuleData] | None
    appLinkData: AppLinkData | None
    rotatingBarcode: RotatingBarcode | None
    heroImage: Image | None
    groupingInfo: GroupingInfo | None
    passConstraints: PassConstraints | None


# @register_model(RegistrationType.WALLETCLASS, "offer")
@register_model("offerClass", has_addmessage=True)
class OfferClass(BaseModel):
    """
    see: https://developers.google.com/wallet/retail/offers/rest/v1/offerclass
    """

    id: str
    title: str | None
    redemptionChannel: RedemptionChannel | None
    provider: str | None
    titleImage: Image | None
    details: str | None
    finePrint: str | None
    helpUri: Uri | None
    localizedTitle: LocalizedString | None
    localizedProvider: LocalizedString | None
    localizedDetails: LocalizedString | None
    localizedFinePrint: LocalizedString | None
    shortTitle: str | None
    localizedShortTitle: LocalizedString | None
    classTemplateInfo: ClassTemplateInfo | None
    version: str | None
    issuerName: str | None
    messages: list[Message] | None
    allowMultipleUsersPerObject: bool = False
    homepageUri: Uri | None
    locations: list[LatLongPoint] | None
    reviewStatus: ReviewStatus
    review: Review | None
    infoModuleData: InfoModuleData | None
    imageModulesData: list[ImageModuleData] | None
    textModulesData: list[TextModuleData] | None
    linksModuleData: LinksModuleData | None
    redemptionIssuers: list[str] | None
    countryCode: str | None
    heroImage: Image | None
    wordMark: Image | None
    enableSmartTap: bool = False
    hexBackgroundColor: str | None
    localizedIssuerName: LocalizedString | None
    multipleDevicesAndHoldersAllowedStatus: MultipleDevicesAndHoldersAllowedStatus | None
    callbackOptions: CallbackOptions | None
    securityAnimation: SecurityAnimation | None
    viewUnlockRequirement: ViewUnlockRequirement | None


# @register_model(RegistrationType.WALLETOBJECT, "offer")
@register_model("offerObject", has_addmessage=True)
class OfferObject(BaseModel):
    """
    see: https://developers.google.com/wallet/retail/offers/rest/v1/offerobject
    """

    id: str
    classId: str
    classReference: OfferClass | None
    version: str | None
    state: State | None
    barcode: Barcode
    messages: list[Message] | None
    validTimeInterval: TimeInterval | None
    locations: list[LatLongPoint] | None
    hasUsers: bool = False
    smartTapRedemptionValue: str
    hasLinkedDevice: bool = False
    disableExpirationNotification: bool = False
    infoModuleData: InfoModuleData | None
    imageModulesData: list[ImageModuleData] | None
    textModulesData: list[TextModuleData] | None
    linksModuleData: LinksModuleData | None
    appLinkData: AppLinkData | None
    rotatingBarcode: RotatingBarcode | None
    heroImage: Image | None
    groupingInfo: GroupingInfo | None
    passConstraints: PassConstraints | None
