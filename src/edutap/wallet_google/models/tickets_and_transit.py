from ..modelbase import GoogleWalletClassModel
from ..modelbase import GoogleWalletMessageable
from ..modelbase import GoogleWalletObjectModel
from ..modelbase import GoogleWalletObjectWithClassReference
from ..modelbase import GoogleWalletStyleableClass
from ..modelbase import GoogleWalletStyleableObject
from ..modelcore import GoogleWalletModel
from ..modelcore import GoogleWalletWithKindModel
from ..registry import register_model
from .primitives import Image
from .primitives import Uri
from .primitives.data import AppLinkData
from .primitives.datetime import TimeInterval
from .primitives.enums import ActivationState
from .primitives.enums import ConcessionCategory
from .primitives.enums import ConfirmationCodeLabel
from .primitives.enums import DoorsOpenLabel
from .primitives.enums import FareClass
from .primitives.enums import FlightStatus
from .primitives.enums import GateLabel
from .primitives.enums import PassengerType
from .primitives.enums import ReviewStatus
from .primitives.enums import RowLabel
from .primitives.enums import SeatLabel
from .primitives.enums import SectionLabel
from .primitives.enums import State
from .primitives.enums import TicketStatus
from .primitives.enums import TransitType
from .primitives.enums import TripType
from .primitives.localized_string import LocalizedString
from .primitives.location import LatLongPoint
from .primitives.money import Money
from .primitives.review import Review
from pydantic import BaseModel
from pydantic import Field

import datetime


class TicketAndTransitClassBaseModel(GoogleWalletClassModel):
    """
    Common Fields for Classes in this Module
    """

    issuerName: str | None = None
    localizedIssuerName: LocalizedString | None = None
    homepageUri: Uri | None = None


class EventVenue(GoogleWalletWithKindModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass#eventvenue
    """

    kind: str | None = Field(
        description="deprecated",
        exclude=True,
        default="walletobjects#eventDateTime",
    )
    name: LocalizedString | None = None
    address: LocalizedString | None = None


class EventDateTime(GoogleWalletWithKindModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass#eventdatetime
    """

    kind: str | None = Field(
        description="deprecated",
        exclude=True,
        default="walletobjects#eventDateTime",
    )
    doorsOpen: datetime.datetime | None = None
    start: datetime.datetime | None = None
    end: datetime.datetime | None = None
    doorsOpenLabel: DoorsOpenLabel | None = None
    customDoorsOpenLabel: LocalizedString | None = None


class EventSeat(BaseModel):
    seat: LocalizedString | None = None
    row: LocalizedString | None = None
    section: LocalizedString | None = None
    gate: LocalizedString | None = None


class EventReservationInfo(BaseModel):
    confirmationCode: str | None = None


@register_model(
    "EventTicketClass",
    url_part="eventTicketClass",
    plural="eventTicketClasses",
    can_disable=False,
)
class EventTicketClass(
    TicketAndTransitClassBaseModel,
    GoogleWalletMessageable,
    GoogleWalletStyleableClass,
):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass
    """

    kind: str | None = Field(
        description="deprecated",
        exclude=True,
        default="walletobjects#eventTicketClass",
    )
    eventName: LocalizedString | None = None
    eventId: str | None = Field(default=None, max_length=64)
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


@register_model(
    "EventTicketObject",
    url_part="eventTicketObject",
    plural="eventTicketObjects",
)
class EventTicketObject(
    GoogleWalletObjectModel,
    GoogleWalletObjectWithClassReference,
    GoogleWalletMessageable,
    GoogleWalletStyleableObject,
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


class ActivationOptions(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitclass#activationoptions
    """

    activationUrl: str | None = None
    allowReactivation: bool = False


class ActivationStatus(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitobject#activationstatus
    """

    state: ActivationState = ActivationState.UNKNOWN_STATE


class TicketRestrictions(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitobject#ticketrestrictions
    """

    routeRestrictions: LocalizedString | None = None
    routeRestrictionsDetails: LocalizedString | None = None
    timeRestrictions: LocalizedString | None = None
    otherRestrictions: LocalizedString | None = None


class TicketCost(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitobject#ticketcost
    """

    faceValue: Money | None = None
    purchasePrice: Money | None = None
    discountMessage: LocalizedString | None = None


class TicketSeat(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitobject#ticketseat
    """

    fareClass: FareClass = FareClass.FARE_CLASS_UNSPECIFIED
    customFareClass: LocalizedString | None = None
    coach: str | None = None
    seat: str | None = None
    seatAssignment: LocalizedString | None = None


class TicketLeg(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitobject#ticketleg
    """

    originStationCod: str | None = None
    originName: LocalizedString | None = None
    destinationStationCode: str | None = None
    destinationName: LocalizedString | None = None
    departureDateTime: str | None = None
    arrivalDateTime: str | None = None
    fareName: LocalizedString | None = None
    carriage: str | None = None
    platform: str | None = None
    zone: str | None = None
    ticketSeat: TicketSeat | None = None
    ticketSeats: list[TicketSeat] | None = None
    transitOperatorName: LocalizedString | None = None
    transitTerminusName: LocalizedString | None = None


class PurchaseDetails(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitobject#purchasedetails
    """

    purchaseReceiptNumber: str | None = None
    purchaseDateTime: str | None = None
    accountId: str | None = None
    confirmationCode: str | None = None
    ticketCost: TicketCost | None = None


class DeviceContext(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitobject#devicecontext
    """

    deviceToken: str | None = None


@register_model(
    "TransitClass",
    url_part="transitClass",
    plural="transitClasses",
)
class TransitClass(GoogleWalletClassModel, GoogleWalletStyleableClass):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitclass
    """

    transitOperatorName: LocalizedString | None = None
    transitType: TransitType = TransitType.TRANSIT_TYPE_UNSPECIFIED
    watermark: Image | None = None
    languageOverride: str | None = None
    customTransitTerminusNameLabel: LocalizedString | None = None
    customTicketNumberLabel: LocalizedString | None = None
    customRouteRestrictionsLabel: LocalizedString | None = None
    customRouteRestrictionsDetailsLabel: LocalizedString | None = None
    customTimeRestrictionsLabel: LocalizedString | None = None
    customOtherRestrictionsLabel: LocalizedString | None = None
    customPurchaseReceiptNumberLabel: LocalizedString | None = None
    customConfirmationCodeLabel: LocalizedString | None = None
    customPurchaseFaceValueLabel: LocalizedString | None = None
    customPurchasePriceLabel: LocalizedString | None = None
    customDiscountMessageLabel: LocalizedString | None = None
    customCarriageLabel: LocalizedString | None = None
    customSeatLabel: LocalizedString | None = None
    customCoachLabel: LocalizedString | None = None
    customPlatformLabel: LocalizedString | None = None
    customZoneLabel: LocalizedString | None = None
    customFareClassLabel: LocalizedString | None = None
    customConcessionCategoryLabel: LocalizedString | None = None
    customFareNameLabel: LocalizedString | None = None
    enableSingleLegItinerary: bool = False
    issuerName: str | None = None
    localizedIssuerName: LocalizedString | None = None
    activationOptions: ActivationOptions | None = None


@register_model(
    "TransitObject",
    url_part="transitObject",
    plural="transitObjects",
)
class TransitObject(GoogleWalletObjectModel, GoogleWalletStyleableObject):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitobject
    """

    classReference: TransitClass | None = None
    ticketNumber: str | None = None
    passengerType: PassengerType = PassengerType.PASSENGER_TYPE_UNSPECIFIED
    passengerNames: str | None = None
    tripId: str | None = None
    ticketStatus: TicketStatus = TicketStatus.TICKET_STATUS_UNSPECIFIED
    customTicketStatus: LocalizedString | None = None
    concessionCategory: ConcessionCategory = (
        ConcessionCategory.CONCESSION_CATEGORY_UNSPECIFIED
    )
    customConcessionCategory: LocalizedString | None = None
    ticketRestrictions: TicketRestrictions | None = None
    purchaseDetails: PurchaseDetails | None = None
    ticketLeg: TicketLeg | None = None
    ticketLegs: list[TicketLeg] | None = None
    tripType: TripType = TripType.TRIP_TYPE_UNSPECIFIED
    validTimeInterval: TimeInterval | None = None
    activationStatus: ActivationStatus | None = None
    deviceContext: DeviceContext | None = None


class FlightCarrier(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/flightclass#flightcarrier
    """

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default="walletobjects#flightCarrier",
    )
    carrierIataCode: str | None = Field(
        max_length=2,
        default=None,
    )
    carrierIcaoCode: str | None = Field(
        max_length=3,
        default=None,
    )
    airlineName: LocalizedString | None = None
    arilineLogo: Image | None = None
    airlineAllianceLogo: Image | None = None
    wideAirlineLogo: Image | None = None


class FlightHeader(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/flightclass#flightheader
    """

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default="walletobjects#flightHeader",
    )
    carrier: FlightCarrier | None = None
    operatingCarrier: FlightCarrier | None = None
    flightNumber: str | None = None
    operatingFlightNumber: str | None = None
    flightNumberDisplayOverride: str | None = None


class AirportInfo(GoogleWalletModel):
    """
    see:
    """


class BoardingAndSeatingPolicy(GoogleWalletModel):
    """
    see:
    """


@register_model(
    "FlightClass",
    url_part="flightClass",
    plural="flightClasses",
)
class FlightClass(GoogleWalletClassModel, GoogleWalletStyleableClass):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/flightclass
    """

    kind: str | None = Field(
        description="deprecated",
        exclude=True,
        default="walletobjects#flightClass",
    )
    localScheduledDepartureDateTime: str | None = Field(default=None)
    localEstimatedOrActualDepartureDateTime: str | None = Field(default=None)
    localBoardingDateTime: str | None = Field(default=None)
    localScheduledArrivalDateTime: str | None = Field(default=None)
    localEstimatedOrActualArrivalDateTime: str | None = Field(default=None)
    flightHeader: FlightHeader
    origin: AirportInfo
    destination: AirportInfo
    flightStatus: FlightStatus = FlightStatus.FLIGHT_STATUS_UNSPECIFIED
    boardingAndSeatingPolicy: BoardingAndSeatingPolicy | None = None
    localGateClosingDateTime: str | None = Field(default=None)
    languageOverride: str | None = None


@register_model(
    "FlightObject",
    url_part="flightObject",
    plural="flightObjects",
)
class FlightObject(GoogleWalletObjectModel, GoogleWalletStyleableObject):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/flightobject
    """

    kind: str | None = Field(
        description="deprecated",
        exclude=True,
        default="walletobjects#flightObject",
    )
    classReference: FlightClass | None = None
