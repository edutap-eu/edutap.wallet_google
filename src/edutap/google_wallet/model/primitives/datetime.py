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

    kind: str | None = "walletobjects#eventDateTime"  # deprecated
    doorsOpen: datetime.datetime | None
    start: datetime.datetime | None
    end: datetime.datetime | None
    doorsOpenLabel: DoorsOpenLabel | None
    customDoorsOpenLabel: LocalizedString | None


class TimeInterval(BaseModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/TimeInterval
    """

    kind: str | None = "walletobjects#timeInterval"  # deprecated
    start: DateTime
    end: DateTime
