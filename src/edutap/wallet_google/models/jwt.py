from ..registry import register_model
from .bases import Model
from .passes import generic
from .passes import retail
from .passes import tickets_and_transit


@register_model(
    "Jwt",
    url_part="jwt",
    can_read=False,
    can_update=False,
    can_disable=False,
    can_list=False,
    can_message=False,
)
class JwtResource(Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/jwt
         https://developers.google.com/wallet/tickets/events/rest/v1/jwt
         https://developers.google.com/wallet/generic/web/javascript-button#google-pay-api-for-passes-jwt
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-12-11

    jwt: str


class Resources(Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/jwt/insert
         https://developers.google.com/wallet/tickets/events/rest/v1/jwt/insert#resources
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-12-11

    eventTicketClasses: list[tickets_and_transit.EventTicketClass] | None = None
    eventTicketObjects: list[tickets_and_transit.EventTicketObject] | None = None
    flightClasses: list[tickets_and_transit.FlightClass] | None = None
    flightObjects: list[tickets_and_transit.FlightObject] | None = None
    giftCardClasses: list[retail.GiftCardClass] | None = None
    giftCardObjects: list[retail.GiftCardObject] | None = None
    loyaltyClasses: list[retail.LoyaltyClass] | None = None
    loyaltyObjects: list[retail.LoyaltyObject] | None = None
    offerClasses: list[retail.OfferClass] | None = None
    offerObjects: list[retail.OfferObject] | None = None
    transitClasses: list[tickets_and_transit.TransitClass] | None = None
    transitObjects: list[tickets_and_transit.TransitObject] | None = None
    genericClasses: list[generic.GenericClass] | None = None
    genericObjects: list[generic.GenericObject] | None = None


class JwtResponse(Model):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/jwt/insert
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-12-11

    saveUri: str
    resources: Resources
