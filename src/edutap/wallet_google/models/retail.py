from ..modelbase import GoogleWalletClassModel
from ..modelbase import GoogleWalletMessageableMixin
from ..modelbase import GoogleWalletObjectModel
from ..modelbase import GoogleWalletObjectWithClassReferenceMixin
from ..modelbase import GoogleWalletStyleableClassMixin
from ..modelbase import GoogleWalletStyleableObjectMixin
from ..modelcore import GoogleWalletModel
from ..modelcore import GoogleWalletWithIdModel
from ..modelcore import GoogleWalletWithKindMixin
from ..registry import register_model
from .primitives import GroupingInfo
from .primitives import Image
from .primitives import PassConstraints
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
from .primitives.enums import RedemptionChannel
from .primitives.enums import ReviewStatus
from .primitives.enums import State
from .primitives.localized_string import LocalizedString
from .primitives.location import LatLongPoint
from .primitives.message import Message
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
    GoogleWalletWithKindMixin,
    GoogleWalletMessageableMixin,
    GoogleWalletStyleableClassMixin,
):
    """
    see: https://developers.google.com/wallet/retail/gift-cards/rest/v1/giftcardclass
    """

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default="walletobjects#giftCardClass",
    )

    merchantName: str | None = None
    programLogo: Image | None = None
    wideProgramLogo: Image | None = None
    pinLabel: str | None = None
    eventNumberLabel: str | None = None
    localizedMerchantName: LocalizedString | None = None
    localizedPinLabel: LocalizedString | None = None
    localizedEventNumberLabel: LocalizedString | None = None
    cardNumberLabel: str | None = None
    localizedCardNumberLabel: LocalizedString | None = None
    version: str | None = Field(description="deprecated", exclude=True, default=None)
    issuerName: str
    localizedIssuerName: LocalizedString | None = None
    homepageUri: Uri | None = None
    locations: list[LatLongPoint] | None = None
    reviewStatus: ReviewStatus = ReviewStatus.REVIEW_STATUS_UNSPECIFIED
    review: Review | None = None
    countryCode: str | None = None
    allowBarcodeRedemption: bool = False


@register_model("GiftCardObject", url_part="giftCardObject")
class GiftCardObject(
    GoogleWalletObjectModel,
    GoogleWalletWithIdModel,
    GoogleWalletWithKindMixin,
    GoogleWalletMessageableMixin,
    GoogleWalletStyleableObjectMixin,
):
    """
    see: https://developers.google.com/wallet/retail/gift-cards/rest/v1/giftcardobject
    """

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
    version: str | None = None
    state: State = State.STATE_UNSPECIFIED
    validTimeInterval: TimeInterval | None = None
    locations: list[LatLongPoint] | None = None
    hasUsers: bool = False
    smartTapRedemptionLevel: str | None = None
    hasLinkedDevice: bool = False
    disableExpirationNotification: bool | None = False
    appLinkData: AppLinkData | None = None


@register_model(
    "LoyaltyClass", url_part="loyaltyClass", plural="loyaltyClasses", can_disable=False
)
class LoyaltyClass(
    GoogleWalletClassModel,
    GoogleWalletWithKindMixin,
    GoogleWalletMessageableMixin,
    GoogleWalletStyleableClassMixin,
):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyclass
    """

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default="walletobjects#loyaltyClass",
    )

    issuerName: str | None = None
    programName: str | None = None
    programLogo: Image | None = None
    logo: Image | None = Field(
        alias="programLogo", serialization_alias="programLogo", default=None
    )
    wideLogo: Image | None = Field(
        alias="wideProgramLogo", serialization_alias="wideProgramLogo", default=None
    )

    reviewStatus: ReviewStatus = ReviewStatus.REVIEW_STATUS_UNSPECIFIED
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
    homepageUri: Uri | None = None
    locations: list[LatLongPoint] | None = None
    review: Review | None = None
    countryCode: str | None = None

    # deprecated
    version: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default=None,
    )  # int64
    allowMultipleUsersPerObject: bool = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default=True,
    )
    infoModuleData: InfoModuleData | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default=None,
    )
    wordMark: Image | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default=None,
    )


class LoyaltyPointsBalance(
    GoogleWalletModel,
    GoogleWalletWithKindMixin,
):
    """
    data-type,
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyobject#LoyaltyPointsBalance
    """

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default="walletobjects#loyaltyPointsBalance",
    )

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
    GoogleWalletWithKindMixin,
):
    """
    data-type,
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyobject#LoyaltyPoints
    """

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default="walletobjects#loyaltyPoints",
    )

    label: str | None = None
    balance: LoyaltyPointsBalance | None = None
    localizedLabel: LocalizedString | None = None


@register_model("LoyaltyObject", url_part="loyaltyObject", plural="loyaltyObjects")
class LoyaltyObject(
    GoogleWalletObjectModel,
    GoogleWalletWithKindMixin,
    GoogleWalletObjectWithClassReferenceMixin,
):
    """
    data-type,
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyobject
    """

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default="walletobjects#loyaltyObject",
    )

    classReference: LoyaltyClass | None = None
    state: State = State.STATE_UNSPECIFIED
    accountName: str | None = None
    accountId: str | None = None
    loyaltyPoints: LoyaltyPoints | None = None
    linkedOfferIds: list[str] | None = None
    secondaryLoyaltyPoints: LoyaltyPoints | None = None
    messages: list[Message] | None = None
    validTimeInterval: TimeInterval | None = None
    locations: list[LatLongPoint] | None = None
    hasUsers: bool | None = None
    smartTapRedemptionValue: str | None = None
    hasLinkedDevice: bool | None = None
    disableExpirationNotification: bool | None = False
    imageModule: ImageModuleData | None = None
    imagesModuleData: list[ImageModuleData] | None = None
    textModulesData: list[TextModuleData] | None = None
    appLinkData: AppLinkData | None = None
    groupingInfo: GroupingInfo | None = None
    passConstraints: PassConstraints | None = None


@register_model(
    "OfferClass", url_part="offerClass", plural="offerClasses", can_disable=False
)
class OfferClass(
    GoogleWalletClassModel,
    GoogleWalletWithKindMixin,
):
    """
    see: https://developers.google.com/wallet/retail/offers/rest/v1/offerclass
    """

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
    classTemplateInfo: ClassTemplateInfo | None = None
    version: str | None = None
    issuerName: str | None = None
    messages: list[Message] | None = None
    allowMultipleUsersPerObject: bool = False
    homepageUri: Uri | None = None
    locations: list[LatLongPoint] | None = None
    reviewStatus: ReviewStatus = ReviewStatus.REVIEW_STATUS_UNSPECIFIED
    review: Review | None = None
    infoModuleData: InfoModuleData | None = None
    imageModulesData: list[ImageModuleData] | None = None
    textModulesData: list[TextModuleData] | None = None
    linksModuleData: LinksModuleData | None = None
    redemptionIssuers: list[str] | None = None
    countryCode: str | None = None
    wordMark: Image | None = None
    enableSmartTap: bool = False
    hexBackgroundColor: str | None = None
    localizedIssuerName: LocalizedString | None = None


@register_model("OfferObject", url_part="offerObject")
class OfferObject(
    GoogleWalletObjectModel,
    GoogleWalletWithKindMixin,
):
    """
    see: https://developers.google.com/wallet/retail/offers/rest/v1/offerobject
    """

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default="walletobjects#offerClass",
    )

    classReference: OfferClass | None = None

    version: str | None = None
    state: State = State.STATE_UNSPECIFIED
    barcode: Barcode
    messages: list[Message] | None = None
    validTimeInterval: TimeInterval | None = None
    locations: list[LatLongPoint] | None = None
    hasUsers: bool = False
    smartTapRedemptionValue: str
    hasLinkedDevice: bool = False
    disableExpirationNotification: bool | None = False
    infoModuleData: InfoModuleData | None = None
    imageModulesData: list[ImageModuleData] | None = None
    textModulesData: list[TextModuleData] | None = None
    linksModuleData: LinksModuleData | None = None
    appLinkData: AppLinkData | None = None
    rotatingBarcode: RotatingBarcode | None = None
    heroImage: Image | None = None
    groupingInfo: GroupingInfo | None = None
    passConstraints: PassConstraints | None = None
