from ..bases import Model
from ..deprecated import DeprecatedKindFieldMixin
from .enums import DoorsOpenLabel
from .general import LocalizedString

import datetime


# Attribute order as in Google's documentation to make future updates easier!
# last check: 2025-01-22


class EventVenue(DeprecatedKindFieldMixin, Model):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass#eventvenue
    """

    # inherits kind (deprecated)
    name: LocalizedString | None = None
    address: LocalizedString | None = None


class EventDateTime(DeprecatedKindFieldMixin, Model):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass#eventdatetime
    """

    # inherits kind (deprecated)
    # TODO: can't be properly resolved because we have a custom module named datetime, i.e. global datetime is shadowed
    doorsOpen: datetime.datetime | None = None
    start: datetime.datetime | None = None
    end: datetime.datetime | None = None
    doorsOpenLabel: DoorsOpenLabel | None = None
    customDoorsOpenLabel: LocalizedString | None = None


class EventSeat(DeprecatedKindFieldMixin, Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/eventticketobject#eventseat
    """

    # inherits kind (deprecated)
    seat: LocalizedString | None = None
    row: LocalizedString | None = None
    section: LocalizedString | None = None
    gate: LocalizedString | None = None


class EventReservationInfo(DeprecatedKindFieldMixin, Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/eventticketobject#eventreservationinfo
    """

    # inherits kind (deprecated)
    confirmationCode: str | None = None
