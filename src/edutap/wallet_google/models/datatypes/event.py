from ..bases import Model
from .enums import DoorsOpenLabel
from .general import LocalizedString

import datetime


class EventVenue(Model):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass#eventvenue
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    name: LocalizedString | None = None
    address: LocalizedString | None = None


class EventDateTime(Model):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass#eventdatetime
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    doorsOpen: datetime.datetime | None = None
    start: datetime.datetime | None = None
    end: datetime.datetime | None = None
    doorsOpenLabel: DoorsOpenLabel | None = None
    customDoorsOpenLabel: LocalizedString | None = None


class EventSeat(Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/eventticketobject#eventseat
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    seat: LocalizedString | None = None
    row: LocalizedString | None = None
    section: LocalizedString | None = None
    gate: LocalizedString | None = None


class EventReservationInfo(Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/eventticketobject#eventreservationinfo
    """

    confirmationCode: str | None = None
