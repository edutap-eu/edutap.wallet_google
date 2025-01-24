"""
Models to be used to assemble the JWT for the save link (add to wallet link).
"""

from ..bases import Model
from ..passes import generic
from ..passes import retail
from ..passes import tickets_and_transit
from ..passes.bases import Reference
from datetime import datetime


# Attribute order as in Google's documentation to make future updates easier!
# last check: 2025-01-22


class JWTPayload(Model):

    eventTicketClasses: (
        list[tickets_and_transit.EventTicketClass | Reference] | None
    ) = None
    eventTicketObjects: (
        list[tickets_and_transit.EventTicketObject | Reference] | None
    ) = None
    flightClasses: list[tickets_and_transit.FlightClass | Reference] | None = None
    flightObjects: list[tickets_and_transit.FlightObject | Reference] | None = None
    giftCardClasses: list[retail.GiftCardClass | Reference] | None = None
    giftCardObjects: list[retail.GiftCardObject | Reference] | None = None
    loyaltyClasses: list[retail.LoyaltyClass | Reference] | None = None
    loyaltyObjects: list[retail.LoyaltyObject | Reference] | None = None
    offerClasses: list[retail.OfferClass | Reference] | None = None
    offerObjects: list[retail.OfferObject | Reference] | None = None
    transitClasses: list[tickets_and_transit.TransitClass | Reference] | None = None
    transitObjects: list[tickets_and_transit.TransitObject | Reference] | None = None
    genericClasses: list[generic.GenericClass | Reference] | None = None
    genericObjects: list[generic.GenericObject | Reference] | None = None


class JWTClaims(Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/Jwt

    Note: `exp` is added to the model as standard field of the JWT specification,
    see https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.4,
    but it is not documented in the Google Wallet JWT Specification!
    """

    iss: str
    aud: str = "google"
    typ: str = "savetowallet"
    iat: str | datetime = ""
    payload: JWTPayload
    origins: list[str]

    # a standard field in the JWT Specification, but not documented for the Google Wallet JWT:
    exp: str | datetime = ""
