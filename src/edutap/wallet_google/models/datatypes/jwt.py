"""
Models to be used to assemble the JWT for the save link (add to wallet link).
"""

from ..bases import Model
from ..bases import WithIdModel
from ..passes import generic
from ..passes import retail
from ..passes import tickets_and_transit
from pydantic import Field
from pydantic import model_validator


class Reference(WithIdModel):
    """
    References an existing wallet object.

    It is used to create the JWT for the add to wallet link.
    The id must be an existing wallet object id.

    Either model_name or mode_type must be set.
    """

    # inherits id

    # mode_name and model_type are implementation specific for this package
    model_name: str | None = Field(exclude=True, default=None)
    model_type: type[Model] | None = Field(exclude=True, default=None)

    @model_validator(mode="after")
    def check_one_of(self) -> "Reference":
        if self.model_name is None and self.model_type is None:
            raise ValueError("One of [model_name, model_type] must be set")
        if self.model_name is not None and self.model_type is not None:
            raise ValueError("Only one of [model_name, model_type] must be set")
        return self


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
    """

    iss: str
    aud: str = "google"
    typ: str = "savettowallet"
    iat: str = ""
    payload: JWTPayload
    origins: list[str]
