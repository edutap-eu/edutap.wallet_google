from .enums import DoorsOpenLabel
from .localized_string import LocalizedString
from pydantic import BaseModel

import datetime


class DateTime(BaseModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/DateTime
    """

    date: datetime.datetime


class EventDateTime(BaseModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/eventticketclass#eventdatetime
    """

    doorsOpen: datetime.datetime | None = None
    start: datetime.datetime | None = None
    end: datetime.datetime | None = None
    doorsOpenLabel: DoorsOpenLabel | None = None
    customDoorsOpenLabel: LocalizedString | None = None


class TimeInterval(BaseModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/TimeInterval
    """

    start: DateTime
    end: DateTime
