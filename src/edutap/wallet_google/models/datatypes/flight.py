from ..bases import Model
from ..deprecated import DeprecatedKindFieldMixin
from .enums import BoardingPolicy
from .enums import SeatClassPolicy
from .general import Image
from .general import LocalizedString
from pydantic import Field


# Attribute order as in Google's documentation to make future updates easier!
# last check: 2025-01-22


class FlightCarrier(DeprecatedKindFieldMixin, Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/flightclass#flightcarrier
    """

    # inherits kind (deprecated)
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


class FlightHeader(DeprecatedKindFieldMixin, Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/flightclass#flightheader
    """

    # inherits kind (deprecated)
    carrier: FlightCarrier | None = None
    flightNumber: str | None = None
    operatingCarrier: FlightCarrier | None = None
    operatingFlightNumber: str | None = None
    flightNumberDisplayOverride: str | None = None


class AirportInfo(DeprecatedKindFieldMixin, Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/flightclass#airportinfo
    """

    # inherits kind (deprecated)
    airportIataCode: str | None = Field(max_length=3, default=None)
    terminal: str | None = None
    gate: str | None = None
    airportNameOverride: LocalizedString | None = None


class BoardingAndSeatingPolicy(DeprecatedKindFieldMixin, Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/flightclass#boardingandseatingpolicy
    """

    # inherits kind (deprecated)
    boardingPolicy: BoardingPolicy = BoardingPolicy.BOARDING_POLICY_UNSPECIFIED
    seatClassPolicy: SeatClassPolicy = SeatClassPolicy.SEAT_CLASS_POLICY_UNSPECIFIED
