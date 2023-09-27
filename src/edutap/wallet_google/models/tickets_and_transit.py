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
from .primitives.datetime import EventDateTime
from .primitives.datetime import TimeInterval
from .primitives.enums import ConfirmationCodeLabel
from .primitives.enums import GateLabel
from .primitives.enums import MultipleDevicesAndHoldersAllowedStatus
from .primitives.enums import ReviewStatus
from .primitives.enums import RowLabel
from .primitives.enums import SeatLabel
from .primitives.enums import SectionLabel
from .primitives.enums import State
from .primitives.enums import ViewUnlockRequirement
from .primitives.localized_string import LocalizedString
from .primitives.location import EventVenue
from .primitives.location import LatLongPoint
from .primitives.money import Money
from .primitives.notification import Message
from .primitives.review import Review
from pydantic import BaseModel
from pydantic import Field


@register_model(
    "EventTicketClass",
    url_part="eventTicketClass",
    plural="eventTicketClasses",
    can_disable=False,
)
class EventTicketClass(GoogleWalletClassModel):
    eventName: LocalizedString | None = None
    eventId: str | None = None
    logo: Image | None = None
    venue: EventVenue | None = None
    dateTime: EventDateTime | None = None
    confirmationCodeLabel: ConfirmationCodeLabel | None = None
    customConfirmationCodeLabel: LocalizedString | None = None
    seatLabel: SeatLabel | None = None
    customSeatLabel: LocalizedString | None = None
    rowLabel: RowLabel | None = None
    customRowLabel: LocalizedString | None = None
    sectionLabel: SectionLabel | None = None
    customSectionLabel: LocalizedString | None = None
    gateLabel: GateLabel | None = None
    customGateLabel: LocalizedString | None = None
    finePrint: LocalizedString | None = None
    classTemplateInfo: ClassTemplateInfo | None = None
    version: str | None = Field(description="deprecated", exclude=True, default=None)
    issuerName: str | None = None
    messages: list[Message] | None = None
    allowMultipleUsersPerObject: bool = Field(
        description="deprecated", default=False, exclude=True
    )
    homepageUri: Uri | None = None
    locations: list[LatLongPoint] | None = None
    reviewStatus: ReviewStatus | None = None
    review: Review | None = None
    infoModuleData: InfoModuleData | None = Field(
        description="deprecated", exclude=True, default=None
    )
    imageModulesData: list[ImageModuleData] | None = None
    textModulesDate: list[TextModuleData] | None = None
    linksModuleData: LinksModuleData | None = None
    redemptionIssuers: list[str] | None = None
    countryCode: str | None = None
    heroImage: Image | None = None
    wordMark: Image | None = Field(description="deprecated", exclude=True, default=None)
    enableSmartTap: bool = False
    hexBackgroundColor: str | None = None
    localizedIssuerName: LocalizedString | None = None
    multipleDevicesAndHoldersAllowedStatus: MultipleDevicesAndHoldersAllowedStatus | None = (
        MultipleDevicesAndHoldersAllowedStatus.STATUS_UNSPECIFIED
    )
    callbackOptions: CallbackOptions | None = None
    securityAnimation: SecurityAnimation | None = None
    viewUnlockRequirement: ViewUnlockRequirement = (
        ViewUnlockRequirement.VIEW_UNLOCK_REQUIREMENT_UNSPECIFIED
    )


class EventSeat(BaseModel):
    seat: LocalizedString | None = None
    row: LocalizedString | None = None
    section: LocalizedString | None = None
    gate: LocalizedString | None = None


class EventReservationInfo(BaseModel):
    confirmationCode: str | None = None


@register_model("EventTicketObject", url_part="eventTicketObject", plural="eventTicketObjects")
class EventTicketObject(GoogleWalletObjectModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketobject
    """

    classReference: EventTicketClass | None = None
    seatInfo: EventSeat | None = None
    reservationInfo: EventReservationInfo | None = None
    ticketHolderName: str | None = None
    ticketNumber: str | None = None
    ticketType: LocalizedString | None = None
    faceValue: Money | None = None
    groupingInfo: GroupingInfo | None = None
    linkedOfferIds: list[str] | None = None
    hexBackgroundColor: str | None = None
    version: str | None = Field(description="deprecated", exclude=True, default=None)
    state: State | None = None
    barcode: Barcode | None = None
    messages: list[Message] | None = None
    validTimeInterval: TimeInterval | None = None
    locations: list[LatLongPoint] | None = None
    hasUsers: bool | None = None
    smartTapRedemptionValue: str | None = None
    hasLinkedDevice: bool | None = False
    disableExpirationNotification: bool | None = False
    infoModuleData: InfoModuleData | None = None
    imageModulesData: list[ImageModuleData] | None = None
    textModulesData: list[TextModuleData] | None = None
    linksModuleData: LinksModuleData | None = None
    appLinkData: AppLinkData | None = None
    rotatingBarcode: RotatingBarcode | None = None
    heroImage: Image | None = None
    passConstraints: PassConstraints | None = None
