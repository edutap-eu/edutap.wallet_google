from ..modelbase import GoogleWalletClassModel
from ..modelbase import GoogleWalletObjectModel
from ..registry import register_model
from .primitives import CallbackOptions
from .primitives import GroupingInfo
from .primitives import Image
from .primitives import LocalizedString
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
    eventName: LocalizedString | None
    eventId: str | None
    logo: Image | None
    venue: EventVenue | None
    dateTime: EventDateTime | None
    confirmationCodeLabel: ConfirmationCodeLabel | None
    customConfirmationCodeLabel: LocalizedString | None
    seatLabel: SeatLabel | None
    customSeatLabel: LocalizedString | None
    rowLabel: RowLabel | None
    customRowLabel: LocalizedString | None
    sectionLabel: SectionLabel | None
    customSectionLabel: LocalizedString | None
    gateLabel: GateLabel | None
    customGateLabel: LocalizedString | None
    finePrint: LocalizedString | None
    classTemplateInfo: ClassTemplateInfo | None
    version: str | None = Field(description="deprecated", exclude=True)
    issuerName: str | None
    messages: list[Message] | None
    allowMultipleUsersPerObject: bool = Field(
        description="deprecated", default=False, exclude=True
    )
    homepageUri: Uri | None
    locations: list[LatLongPoint] | None
    reviewStatus: ReviewStatus | None
    review: Review | None
    infoModuleData: InfoModuleData | None = Field(
        description="deprecated", exclude=True
    )
    imageModulesData: list[ImageModuleData] | None
    textModulesDate: list[TextModuleData] | None
    linksModuleData: LinksModuleData | None
    redemptionIssuers: list[str] | None
    countryCode: str | None
    heroImage: Image | None
    wordMark: Image | None = Field(description="deprecated", exclude=True)
    enableSmartTap: bool = False
    hexBackgroundColor: str | None
    localizedIssuerName: LocalizedString | None
    multipleDevicesAndHoldersAllowedStatus: MultipleDevicesAndHoldersAllowedStatus | None = (
        MultipleDevicesAndHoldersAllowedStatus.STATUS_UNSPECIFIED
    )
    callbackOptions: CallbackOptions | None
    securityAnimation: SecurityAnimation | None
    viewUnlockRequirement: ViewUnlockRequirement = (
        ViewUnlockRequirement.VIEW_UNLOCK_REQUIREMENT_UNSPECIFIED
    )


class EventSeat(BaseModel):
    seat: LocalizedString | None
    row: LocalizedString | None
    section: LocalizedString | None
    gate: LocalizedString | None


class EventReservationInfo(BaseModel):
    confirmationCode: str | None


@register_model("EventTicketObject", url_part="eventTicketObject")
class EventTicketObject(GoogleWalletObjectModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketobject
    """

    classReference: EventTicketClass | None
    seatInfo: EventSeat | None
    reservationInfo: EventReservationInfo | None
    ticketHolderName: str | None
    ticketNumber: str | None
    ticketType: LocalizedString | None
    faceValue: Money | None
    groupingInfo: GroupingInfo | None = None
    linkedOfferIds: list[str] | None
    hexBackgroundColor: str | None = None
    version: str | None = Field(description="deprecated", exclude=True)
    state: State | None = None
    barcode: Barcode | None = None
    messages: list[Message] | None
    validTimeInterval: TimeInterval | None = None
    locations: list[LatLongPoint] | None
    hasUsers: bool | None = None
    smartTapRedemptionValue: str | None = None
    hasLinkedDevice: bool | None = False
    disableExpirationNotification: bool | None = False
    infoModuleData: InfoModuleData | None
    imageModulesData: list[ImageModuleData] | None = None
    textModulesData: list[TextModuleData] | None = None
    linksModuleData: LinksModuleData | None = None
    appLinkData: AppLinkData | None = None
    rotatingBarcode: RotatingBarcode | None = None
    heroImage: Image | None = None
    passConstraints: PassConstraints | None
