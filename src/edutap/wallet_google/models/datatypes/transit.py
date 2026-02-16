from ..bases import Model
from ..datatypes.enums import ActivationState
from ..datatypes.money import Money
from .enums import FareClass
from .general import LocalizedString
from pydantic import AnyHttpUrl
from pydantic import model_validator


# Attribute order as in Google's documentation to make future updates easier!
# last check: 2025-01-22


class ActivationOptions(Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitclass#activationoptions
    """

    activationUrl: AnyHttpUrl | None = None
    allowReactivation: bool = False


class ActivationStatus(Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitobject#activationstatus
    """

    state: ActivationState = ActivationState.UNKNOWN_STATE


class TicketRestrictions(Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitobject#ticketrestrictions
    """

    routeRestrictions: LocalizedString | None = None
    routeRestrictionsDetails: LocalizedString | None = None
    timeRestrictions: LocalizedString | None = None
    otherRestrictions: LocalizedString | None = None


class TicketCost(Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitobject#ticketcost
    """

    faceValue: Money | None = None
    purchasePrice: Money | None = None
    discountMessage: LocalizedString | None = None


class TicketSeat(Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitobject#ticketseat
    """

    fareClass: FareClass = FareClass.FARE_CLASS_UNSPECIFIED
    customFareClass: LocalizedString | None = None
    coach: str | None = None
    seat: str | None = None
    seatAssignment: LocalizedString | None = None


class TicketLeg(Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitobject#ticketleg
    """

    originStationCode: str | None = None
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


class PurchaseDetails(Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitobject#purchasedetails
    """

    purchaseReceiptNumber: str | None = None
    purchaseDateTime: str | None = None
    accountId: str | None = None
    confirmationCode: str | None = None
    ticketCost: TicketCost | None = None


class DeviceContext(Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/transitobject#devicecontext
    """

    deviceToken: str | None = None
