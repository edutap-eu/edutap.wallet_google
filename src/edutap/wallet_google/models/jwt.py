from ..modelbase import GoogleWalletClassModel
from ..modelbase import GoogleWalletObjectModel
from ..modelcore import GoogleWalletModel
from ..registry import register_model

# from . import generic
from . import retail
from . import tickets_and_transit


@register_model(
    "Jwt",
    url_part="jwt",
    can_read=False,
    can_update=False,
    can_disable=False,
    can_list=False,
    can_message=False,
)
class JwtResource(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/jwt
         https://developers.google.com/wallet/generic/web/javascript-button#google-pay-api-for-passes-jwt
    """

    jwt: str


class Resources(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/jwt/insert#resources
    """

    # the documentation says nothing about GenericClass/Object here
    # those are probably missing from the documentation, needs verification
    # genericClasses: list[generic.GenericClass] | None = None
    # genericObjects: list[generic.GenericObject] | None = None
    eventTicketClasses: list[tickets_and_transit.EventTicketClass] | None = None
    eventTicketObjects: list[tickets_and_transit.EventTicketObject] | None = None
    flightClasses: list[GoogleWalletClassModel] | None = None
    flightObjects: list[GoogleWalletObjectModel] | None = None
    giftCardClasses: list[retail.GiftCardClass] | None = None
    giftCardObjects: list[retail.GiftCardObject] | None = None
    loyaltyClasses: list[retail.LoyaltyClass] | None = None
    loyaltyObjects: list[retail.LoyaltyObject] | None = None
    offerClasses: list[retail.OfferClass] | None = None
    offerObjects: list[retail.OfferObject] | None = None
    transitClasses: list[GoogleWalletClassModel] | None = None
    transitObjects: list[GoogleWalletObjectModel] | None = None


class JwtResponse(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/jwt/insert
    """

    saveUri: str
    resources: Resources
