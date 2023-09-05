from .localized_string import LocalizedString
from pydantic import BaseModel
from pydantic import ConstrainedFloat


class Latitude(ConstrainedFloat):
    ge = -90.0
    le = 90.0


class Longitude(ConstrainedFloat):
    ge = -180.0
    le = 180.0


class LatLongPoint(BaseModel):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/LatLongPoint
    """

    kind: str | None = "walletobjects#latLongPoint"
    latitude: Latitude
    longitude: Longitude


class EventVenue(BaseModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass#eventvenue
    """

    kind: str | None = "walletobjects#eventVenue"
    name: LocalizedString | None
    address: LocalizedString | None
