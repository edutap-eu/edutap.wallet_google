from ..bases import Model
from pydantic import Field

import datetime


class DateTime(Model):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/DateTime
    """

    date: datetime.datetime


class TimeInterval(Model):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/TimeInterval
    """

    start: DateTime | None = None
    end: DateTime | None = None
