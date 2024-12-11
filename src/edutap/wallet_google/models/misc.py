"""
This module contains models that are not directly related to passes but to other Google Wallet APIs
"""

from ..registry import register_model
from .bases import Model
from .bases import WithIdModel
from .datatypes.general import CallbackOptions
from .datatypes.message import Message
from .datatypes.smarttap import IssuerContactInfo
from .datatypes.smarttap import IssuerToUserInfo
from .datatypes.smarttap import Permission
from .datatypes.smarttap import SmartTapMerchantData
from .passes import generic
from .passes import retail
from .passes import tickets_and_transit
from .passes.bases import ClassModel


class ObjectWithClassReference(WithIdModel):
    """

    Google Wallet Object with a classReferences attribute, that reflects the whole class data.
    This class is used to create the save_link only, never inherit from it.
    """

    classReference: ClassModel | None = None


@register_model(
    "SmartTap",
    url_part="smartTap",
    can_read=False,
    can_update=False,
    can_disable=False,
    can_list=False,
    can_message=False,
)
class SmartTap(WithIdModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/smarttap#resource:-smarttap
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    # inherits id
    merchantId: str
    infos: list[IssuerToUserInfo] | None = None


@register_model(
    "Issuer",
    url_part="issuer",
    resource_id="issuerId",
    can_message=False,
)
class Issuer(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/issuer
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    issuerId: str
    name: str
    contactInfo: IssuerContactInfo | None = None
    homepageUrl: str | None = None
    smartTapMerchantData: SmartTapMerchantData | None = None
    callbackOptions: CallbackOptions | None = None


@register_model(
    "Permissions",
    url_part="permissions",
    resource_id="issuerId",
    can_disable=False,
    can_list=False,
    can_message=False,
)
class Permissions(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/permissions
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    issuerId: str | None = None
    permissions: list[Permission] = []


class AddMessageRequest(Model):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/AddMessageRequest
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    message: Message | None = None


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
