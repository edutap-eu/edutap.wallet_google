from ..modelbase import GoogleWalletClassModel
from ..modelbase import GoogleWalletMessageable
from ..modelbase import GoogleWalletObjectModel
from ..modelbase import GoogleWalletObjectWithClassReference
from ..modelbase import GoogleWalletStyleable
from ..registry import register_model
from .primitives import Uri
from .primitives.data import AppLinkData
from .primitives.datetime import EventDateTime
from .primitives.datetime import TimeInterval
from .primitives.enums import ConfirmationCodeLabel
from .primitives.enums import GateLabel
from .primitives.enums import ReviewStatus
from .primitives.enums import RowLabel
from .primitives.enums import SeatLabel
from .primitives.enums import SectionLabel
from .primitives.enums import State
from .primitives.localized_string import LocalizedString
from .primitives.location import EventVenue
from .primitives.location import LatLongPoint
from .primitives.money import Money
from .primitives.review import Review
from pydantic import BaseModel
from pydantic import Field


@register_model(
    "EventTicketClass",
    url_part="eventTicketClass",
    plural="eventTicketClasses",
    can_disable=False,
)
class EventTicketClass(GoogleWalletClassModel, GoogleWalletMessageable):
    eventName: LocalizedString | None = None
    eventId: str | None = None
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
    version: str | None = Field(description="deprecated", exclude=True, default=None)
    issuerName: str | None = None
    localizedIssuerName: LocalizedString | None = None
    homepageUri: Uri | None = None
    locations: list[LatLongPoint] | None = None
    reviewStatus: ReviewStatus | None = None
    review: Review | None = None
    countryCode: str | None = None


class EventSeat(BaseModel):
    seat: LocalizedString | None = None
    row: LocalizedString | None = None
    section: LocalizedString | None = None
    gate: LocalizedString | None = None


class EventReservationInfo(BaseModel):
    confirmationCode: str | None = None


@register_model(
    "EventTicketObject", url_part="eventTicketObject", plural="eventTicketObjects"
)
class EventTicketObject(
    GoogleWalletObjectModel,
    GoogleWalletObjectWithClassReference,
    GoogleWalletMessageable,
    GoogleWalletStyleable,
):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketobject
    """

    kind: str | None = Field(
        description="deprecated",
        exclude=True,
        default="walletobjects#eventTicketObject",
    )
    classReference: EventTicketClass | None = None
    seatInfo: EventSeat | None = None
    reservationInfo: EventReservationInfo | None = None
    ticketHolderName: str | None = None
    ticketNumber: str | None = None
    ticketType: LocalizedString | None = None
    faceValue: Money | None = None
    linkedOfferIds: list[str] | None = None
    version: str | None = Field(description="deprecated", exclude=True, default=None)
    state: State | None = None
    validTimeInterval: TimeInterval | None = None
    locations: list[LatLongPoint] | None = None
    hasUsers: bool | None = None
    hasLinkedDevice: bool | None = False
    disableExpirationNotification: bool | None = False
    appLinkData: AppLinkData | None = None
