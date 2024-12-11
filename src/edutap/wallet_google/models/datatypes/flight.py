from ..bases import Model
from .enums import BoardingPolicy
from .enums import SeatClassPolicy
from .general import Image
from .general import LocalizedString
from pydantic import Field


class FlightCarrier(Model):
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


class FlightHeader(Model):
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


class AirportInfo(Model):
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


class BoardingAndSeatingPolicy(Model):
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
