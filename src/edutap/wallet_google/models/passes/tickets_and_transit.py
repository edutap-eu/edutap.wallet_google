from ...registry import register_model
from ..datatypes.enums import ConcessionCategory
from ..datatypes.enums import ConfirmationCodeLabel
from ..datatypes.enums import FlightStatus
from ..datatypes.enums import GateLabel
from ..datatypes.enums import NotificationSettingsForUpdates
from ..datatypes.enums import PassengerType
from ..datatypes.enums import ReviewStatus
from ..datatypes.enums import RowLabel
from ..datatypes.enums import SeatLabel
from ..datatypes.enums import SectionLabel
from ..datatypes.enums import TicketStatus
from ..datatypes.enums import TransitType
from ..datatypes.enums import TripType
from ..datatypes.event import EventDateTime
from ..datatypes.event import EventReservationInfo
from ..datatypes.event import EventSeat
from ..datatypes.event import EventVenue
from ..datatypes.flight import AirportInfo
from ..datatypes.flight import BoardingAndSeatingPolicy
from ..datatypes.flight import FlightHeader
from ..datatypes.general import Image
from ..datatypes.general import Uri
from ..datatypes.localized_string import LocalizedString
from ..datatypes.money import Money
from ..datatypes.review import Review
from ..datatypes.transit import ActivationOptions
from ..datatypes.transit import ActivationStatus
from ..datatypes.transit import DeviceContext
from ..datatypes.transit import PurchaseDetails
from ..datatypes.transit import TicketLeg
from ..datatypes.transit import TicketRestrictions
from ..deprecated import DeprecatedAllowMultipleUsersPerObjectMixin
from ..deprecated import DeprecatedInfoModuleDataFieldMixin
from ..deprecated import DeprecatedKindFieldMixin
from ..deprecated import DeprecatedLocationsFieldMixin
from ..deprecated import DeprecatedVersionFieldMixin
from ..deprecated import DeprecatedWordMarkFieldMixin
from .bases import ClassModel
from .bases import CommonLogosMixin
from .bases import ObjectModel
from .bases import StyleableMixin
from pydantic import Field


# Attribute order as in Google's documentation to make future updates easier!
# last check: 2025-01-22


@register_model(
    "EventTicketClass",
    url_part="eventTicketClass",
    plural="eventTicketClasses",
)
class EventTicketClass(
    DeprecatedKindFieldMixin,
    DeprecatedVersionFieldMixin,
    DeprecatedAllowMultipleUsersPerObjectMixin,
    DeprecatedLocationsFieldMixin,
    DeprecatedInfoModuleDataFieldMixin,
    DeprecatedWordMarkFieldMixin,
    StyleableMixin,
    CommonLogosMixin,
    ClassModel,
):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass
    """

    # inherits kind (deprecated)
    eventName: LocalizedString | None = None
    eventId: str | None = Field(default=None, max_length=64)
    # inherits logo
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
    # inherits version (deprecated)
    issuerName: str | None = None
    # inherits messages
    # inherits allowMultipleUsersPerObject (deprecated)
    homepageUri: Uri | None = None
    # inherits locations (deprecated)
    reviewStatus: ReviewStatus | None = None
    review: Review | None = None
    # inherits infoModuleData (deprecated)
    # inherits imageModulesData
    # inherits textModulesData
    # inherits linksModuleData
    # inherits redemptionIssuers
    countryCode: str | None = None
    # inherits heroImage
    # inherits wordMark (deprecated)
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


@register_model("EventTicketObject", url_part="eventTicketObject")
class EventTicketObject(
    DeprecatedKindFieldMixin,
    DeprecatedVersionFieldMixin,
    DeprecatedLocationsFieldMixin,
    DeprecatedInfoModuleDataFieldMixin,
    StyleableMixin,
    CommonLogosMixin,
    ObjectModel,
):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketobject
    """

    # inherits kind (deprecated)
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
    # inherits version (deprecated)
    # inherits state
    # inherits barcode
    # inherits messages
    # inherits validTimeInterval
    # inherits locations (deprecated)
    # inherits hasUsers
    # inherits smartTapRedemptionValue
    hasLinkedDevice: bool | None = False
    disableExpirationNotification: bool | None = False
    # inherits infoModuleData (deprecated)
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


@register_model("TransitClass", url_part="transitClass", plural="transitClasses")
class TransitClass(
    DeprecatedVersionFieldMixin,
    DeprecatedAllowMultipleUsersPerObjectMixin,
    DeprecatedLocationsFieldMixin,
    DeprecatedInfoModuleDataFieldMixin,
    DeprecatedWordMarkFieldMixin,
    StyleableMixin,
    CommonLogosMixin,
    ClassModel,
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
    # inherits version (deprecated)
    issuerName: str | None = None
    # inherits messages
    # inherits allowMultipleUsersPerObject (deprecated)
    homepageUri: Uri | None = None
    # inherits locations (deprecated)
    reviewStatus: ReviewStatus | None = None
    review: Review | None = None
    # inherits infoModuleData (deprecated)
    # inherits imageModulesData
    # inherits textModulesData
    # inherits linksModuleData
    # inherits redemptionIssuers
    countryCode: str | None = None
    # inherits heroImage
    # inherits wordMark (deprecated)
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


@register_model("TransitObject", url_part="transitObject")
class TransitObject(
    DeprecatedVersionFieldMixin,
    DeprecatedLocationsFieldMixin,
    DeprecatedInfoModuleDataFieldMixin,
    StyleableMixin,
    CommonLogosMixin,
    ObjectModel,
):
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
    # TODO: validator: Only one of the two fields should be set, i.e. either customConcessionCategory or concessionCategory
    ticketRestrictions: TicketRestrictions | None = None
    purchaseDetails: PurchaseDetails | None = None
    ticketLeg: TicketLeg | None = None
    ticketLegs: list[TicketLeg] | None = None
    # TODO: validator: If more than one leg is to be specified then use the ticketLegs field instead.
    #                  Both ticketLeg and ticketLegs may not be set.
    # inherits hexBackgroundColor
    tripType: TripType = TripType.TRIP_TYPE_UNSPECIFIED
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
    hasLinkedDevice: bool | None = False
    disableExpirationNotification: bool | None = False
    # inherits infoModuleData (deprecated)
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


@register_model("FlightClass", url_part="flightClass", plural="flightClasses")
class FlightClass(
    DeprecatedKindFieldMixin,
    DeprecatedVersionFieldMixin,
    DeprecatedAllowMultipleUsersPerObjectMixin,
    DeprecatedLocationsFieldMixin,
    DeprecatedInfoModuleDataFieldMixin,
    DeprecatedWordMarkFieldMixin,
    StyleableMixin,
    CommonLogosMixin,
    ClassModel,
):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/flightclass
    """

    # inherits kind (deprecated)
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
    # inherits version (deprecated)
    issuerName: str | None = None
    # inherits messages
    # inherits allowMultipleUsersPerObject (deprecated)
    # inherits homepageUri
    # inherits locations (deprecated)
    reviewStatus: ReviewStatus | None = None
    review: Review | None = None
    # inherits infoModuleData (deprecated)
    # inherits imageModulesData
    # inherits textModulesData
    # inherits linksModuleData
    # inherits redemptionIssuers
    countryCode: str | None = None
    # inherits heroImage
    # inherits wordMark (deprecated)
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


@register_model("FlightObject", url_part="flightObject")
class FlightObject(
    DeprecatedKindFieldMixin,
    DeprecatedVersionFieldMixin,
    DeprecatedLocationsFieldMixin,
    StyleableMixin,
    ObjectModel,
):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/flightobject
    """

    # inherits kind (deprecated)
    classReference: FlightClass | None = None
    passengerName: str | None = None
    # TODO: boardingAndSeatingInfo
    # TODO: reservationInfo
    securityProgramLogo: Image | None = None
    # inherits hexBackgroundColor
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
