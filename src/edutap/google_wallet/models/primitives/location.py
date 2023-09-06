from .localized_string import LocalizedString
from pydantic import BaseModel
from pydantic import Field


class LatLongPoint(BaseModel):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/LatLongPoint
    """

    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)


class EventVenue(BaseModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass#eventvenue
    """

    name: LocalizedString | None
    address: LocalizedString | None
