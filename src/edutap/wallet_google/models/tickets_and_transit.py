from ..registry import register_model
from .bases import GoogleWalletClassModel
from .bases import GoogleWalletCommonLogosMixin
from .bases import GoogleWalletModel
from .bases import GoogleWalletObjectModel
from .bases import GoogleWalletStyleableMixin
from .primitives import Image
from .primitives import Uri
from .primitives.enums import ActivationState
from .primitives.enums import BoardingPolicy
from .primitives.enums import ConcessionCategory
from .primitives.enums import ConfirmationCodeLabel
from .primitives.enums import DoorsOpenLabel
from .primitives.enums import FareClass
from .primitives.enums import FlightStatus
from .primitives.enums import GateLabel
from .primitives.enums import NotificationSettingsForUpdates
from .primitives.enums import PassengerType
from .primitives.enums import ReviewStatus
from .primitives.enums import RowLabel
from .primitives.enums import SeatClassPolicy
from .primitives.enums import SeatLabel
from .primitives.enums import SectionLabel
from .primitives.enums import TicketStatus
from .primitives.enums import TransitType
from .primitives.enums import TripType
from .primitives.localized_string import LocalizedString
from .primitives.location import LatLongPoint
from .primitives.money import Money
from .primitives.review import Review
from pydantic import Field
from pydantic import model_validator

import datetime


class EventVenue(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass#eventvenue
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default="walletobjects#eventDateTime",
    )
    name: LocalizedString | None = None
    address: LocalizedString | None = None


class EventDateTime(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass#eventdatetime
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default="walletobjects#eventDateTime",
    )
    doorsOpen: datetime.datetime | None = None
    start: datetime.datetime | None = None
    end: datetime.datetime | None = None
    doorsOpenLabel: DoorsOpenLabel | None = None
    customDoorsOpenLabel: LocalizedString | None = None


class EventSeat(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/eventticketobject#eventseat
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default="walletobjects#eventSeat",
    )
    seat: LocalizedString | None = None
    row: LocalizedString | None = None
    section: LocalizedString | None = None
    gate: LocalizedString | None = None


class EventReservationInfo(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/eventticketobject#eventreservationinfo
    """

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default="walletobjects#eventReservationInfo",
    )
    confirmationCode: str | None = None


@register_model(
    "EventTicketClass",
    url_part="eventTicketClass",
    plural="eventTicketClasses",
    can_disable=False,
)
class EventTicketClass(
    GoogleWalletClassModel,
    GoogleWalletStyleableMixin,
    GoogleWalletCommonLogosMixin,
):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # Most deprecated are skipped.
    # last check: 2024-11-29

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
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
    # inherits classTemplateInfo
    # inherits id
    issuerName: str | None = None
    # inherits messages
    homepageUri: Uri | None = None
    locations: list[LatLongPoint] | None = Field(default=None, deprecated=True)
    reviewStatus: ReviewStatus | None = None
    review: Review | None = None
    # inherits infoModuleData
    # inherits imageModulesData
    # inherits textModulesData
    # inherits linksModuleData
    # inherits redemptionIssuers
    countryCode: str | None = None
    # inherits heroImage
    # inherits enableSmartTap
    # inherits hexBackgroundColor
    localizedIssuerName: LocalizedString | None = None
    # inherits multipleDevicesAndHoldersAllowedStatus
    # inherits callbackOptions
    # inherits securityAnimation
    # inherits viewUnlockRequirement
    # inherits wideLogo
    notifyPreference: NotificationSettingsForUpdates = (
        NotificationSettingsForUpdates.NOTIFICATION_SETTINGS_FOR_UPDATES_UNSPECIFIED
    )
    # inherits appLinkData
    # inherits valueAddedModuleData


@register_model(
    "EventTicketObject",
    url_part="eventTicketObject",
    plural="eventTicketObjects",
)
class EventTicketObject(
    GoogleWalletObjectModel,
    GoogleWalletStyleableMixin,
    GoogleWalletCommonLogosMixin,
):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketobject
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # Most deprecated are skipped.
    # last check: 2024-11-29

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
    # inherits groupingInfo
    linkedOfferIds: list[str] | None = None
    # inherits hexBackgroundColor
    # inherits id
    # inherits classId
    version: str | None = Field(description="deprecated", exclude=True, default=None)
    # inherits state
    # inherits barcode
    # inherits messages
    # inherits validTimeInterval
    locations: list[LatLongPoint] | None = Field(
        description="deprecated", exclude=True, default=None
    )
    # inherits hasUsers
    # inherits smartTapRedemptionValue
    hasLinkedDevice: bool | None = False
    disableExpirationNotification: bool | None = False
    # inherits infoModuleData
    # inherits imageModulesData
    # inherits textModulesData
    # inherits linksModuleData
    # inherits appLinkData
    # inherits rotatingBarcode
    # inherits heroImage
    # inherits passConstraints
    # inherits saveRestrictions
    # inherits linkedObjectIds
    notifyPreference: NotificationSettingsForUpdates = (
        NotificationSettingsForUpdates.NOTIFICATION_SETTINGS_FOR_UPDATES_UNSPECIFIED
    )
    # inherits valueAddedModuleData


class ActivationOptions(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitclass#activationoptions
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    activationUrl: str | None = None
    allowReactivation: bool = False


class ActivationStatus(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitobject#activationstatus
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    state: ActivationState = ActivationState.UNKNOWN_STATE


class TicketRestrictions(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitobject#ticketrestrictions
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    routeRestrictions: LocalizedString | None = None
    routeRestrictionsDetails: LocalizedString | None = None
    timeRestrictions: LocalizedString | None = None
    otherRestrictions: LocalizedString | None = None


class TicketCost(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitobject#ticketcost
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    faceValue: Money | None = None
    purchasePrice: Money | None = None
    discountMessage: LocalizedString | None = None


class TicketSeat(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitobject#ticketseat
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    fareClass: FareClass = FareClass.FARE_CLASS_UNSPECIFIED
    customFareClass: LocalizedString | None = None
    coach: str | None = None
    seat: str | None = None
    seatAssignment: LocalizedString | None = None


class TicketLeg(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitobject#ticketleg
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

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

    @model_validator(mode="after")
    def check_one_of(self) -> "TicketLeg":
        if self.ticketSeat is None and self.ticketSeats is None:
            return self
        if (
            self.ticketSeat is not None
            and self.ticketSeats
            and len(self.ticketSeats) > 0
        ):
            raise ValueError("Only one of ticketSeat or ticketSeats must be set")
        if self.ticketSeats and len(self.ticketSeats) == 1:
            raise ValueError(
                "If only one seat is to be specified then use the ticketSeat field instead."
            )
        return self


class PurchaseDetails(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitobject#purchasedetails
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    purchaseReceiptNumber: str | None = None
    purchaseDateTime: str | None = None
    accountId: str | None = None
    confirmationCode: str | None = None
    ticketCost: TicketCost | None = None


class DeviceContext(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitobject#devicecontext
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    deviceToken: str | None = None


@register_model(
    "TransitClass",
    url_part="transitClass",
    plural="transitClasses",
)
class TransitClass(
    GoogleWalletClassModel,
    GoogleWalletStyleableMixin,
    GoogleWalletCommonLogosMixin,
):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitclass
    """

    transitOperatorName: LocalizedString | None = None
    # inherits logo
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
    # inherits classTemplateInfo
    enableSingleLegItinerary: bool = False
    # inherits id
    issuerName: str | None = None
    # inherits messages
    homepageUri: Uri | None = None
    reviewStatus: ReviewStatus | None = None
    review: Review | None = None
    # inherits imageModulesData
    # inherits textModulesData
    # inherits linksModuleData
    # inherits redemptionIssuers
    countryCode: str | None = None
    # inherits heroImage
    # inherits enableSmartTap
    # inherits hexBackgroundColor
    localizedIssuerName: LocalizedString | None = None
    # inherits multipleDevicesAndHoldersAllowedStatus
    # inherits callbackOptions
    # inherits securityAnimation
    activationOptions: ActivationOptions | None = None
    # inherits viewUnlockRequirement
    # inherits wideLogo
    notifyPreference: NotificationSettingsForUpdates = (
        NotificationSettingsForUpdates.NOTIFICATION_SETTINGS_FOR_UPDATES_UNSPECIFIED
    )
    # inherits appLinkData
    # inherits valueAddedModuleData


@register_model(
    "TransitObject",
    url_part="transitObject",
    plural="transitObjects",
)
class TransitObject(
    GoogleWalletObjectModel,
    GoogleWalletStyleableMixin,
    GoogleWalletCommonLogosMixin,
):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitobject
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # Most deprecated are skipped.
    # last check: 2024-11-29

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
    # TODO: validator: If more than one leg is to be specified then use the ticketLegs field instead.
    #                  Both ticketLeg and ticketLegs may not be set.
    tripType: TripType = TripType.TRIP_TYPE_UNSPECIFIED
    # inherits id
    # inherits classId
    # inherits state
    # inherits barcode
    # inherits messages
    # inherits validTimeInterval
    # inherits hasUsers
    # inherits smartTapRedemptionValue
    hasLinkedDevice: bool | None = False
    disableExpirationNotification: bool | None = False
    # inherits infoModuleData
    # inherits imageModulesData
    # inherits textModulesData
    # inherits linksModuleData
    # inherits appLinkData
    activationStatus: ActivationStatus | None = None
    # inherits rotatingBarcode
    deviceContext: DeviceContext | None = None
    # inherits heroImage
    # inherits groupingInfo
    # inherits passConstraints
    # inherits saveRestrictions
    # inherits linkedObjectIds
    notifyPreference: NotificationSettingsForUpdates = (
        NotificationSettingsForUpdates.NOTIFICATION_SETTINGS_FOR_UPDATES_UNSPECIFIED
    )
    # inherits valueAddedModuleData


class FlightCarrier(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/flightclass#flightcarrier
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

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
    airlineLogo: Image | None = None
    airlineAllianceLogo: Image | None = None
    wideAirlineLogo: Image | None = None


class FlightHeader(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/flightclass#flightheader
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default="walletobjects#flightHeader",
    )
    carrier: FlightCarrier | None = None
    flightNumber: str | None = None
    operatingCarrier: FlightCarrier | None = None
    operatingFlightNumber: str | None = None
    flightNumberDisplayOverride: str | None = None


class AirportInfo(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/flightclass#airportinfo
    """

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default="walletobjects#airportInfo",
    )
    airportIataCode: str | None = Field(max_length=3, default=None)
    terminal: str | None = None
    gate: str | None = None
    airportNameOverride: LocalizedString | None = None


class BoardingAndSeatingPolicy(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/flightclass#boardingandseatingpolicy
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default="walletobjects#boardingAndSeatingPolicy",
    )
    boardingPolicy: BoardingPolicy = BoardingPolicy.BOARDING_POLICY_UNSPECIFIED
    seatClassPolicy: SeatClassPolicy = SeatClassPolicy.SEAT_CLASS_POLICY_UNSPECIFIED


@register_model(
    "FlightClass",
    url_part="flightClass",
    plural="flightClasses",
)
class FlightClass(
    GoogleWalletClassModel,
    GoogleWalletStyleableMixin,
    GoogleWalletCommonLogosMixin,
):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/flightclass
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # Most deprecated are skipped.
    # last check: 2024-11-29
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
    # inherits classTemplateInfo
    languageOverride: str | None = None
    # inherits id
    issuerName: str | None = None
    # inherits messages
    # inherits homepageUri
    reviewStatus: ReviewStatus | None = None
    review: Review | None = None
    # inherits infoModuleData
    # inherits imageModulesData
    # inherits textModulesData
    # inherits linksModuleData
    # inherits redemptionIssuers
    countryCode: str | None = None
    # inherits heroImage
    # inherits enableSmartTap
    # inherits hexBackgroundColor
    localizedIssuerName: LocalizedString | None = None
    # inherits multipleDevicesAndHoldersAllowedStatus
    # inherits callbackOptions
    # inherits securityAnimation
    # inherits viewUnlockRequirement
    notifyPreference: NotificationSettingsForUpdates = (
        NotificationSettingsForUpdates.NOTIFICATION_SETTINGS_FOR_UPDATES_UNSPECIFIED
    )
    # inherits appLinkData
    # inherits valueAddedModuleData


@register_model(
    "FlightObject",
    url_part="flightObject",
    plural="flightObjects",
)
class FlightObject(GoogleWalletObjectModel, GoogleWalletStyleableMixin):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/flightobject
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29
    kind: str | None = Field(
        description="deprecated",
        exclude=True,
        default="walletobjects#flightObject",
    )
    classReference: FlightClass | None = None
    passengerName: str | None = None
    # TODO boardingAndSeatingInfo
    # TODO reservationInfo
    securityProgramLogo: Image | None = None
    # inherits hexBackgroundColor
    # inherits id
    # inherits classId
    # inherits state
    # inherits barcode
    # inherits messages
    # inherits validTimeInterval
    # inherits hasUsers
    # inherits smartTapRedemptionValue
    hasLinkedDevice: bool | None = False
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
