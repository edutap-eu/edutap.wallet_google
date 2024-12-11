from pydantic import BaseModel
from pydantic import Field

import datetime


class DateTime(BaseModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/DateTime
    """

    date: datetime.datetime


class TimeInterval(BaseModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/TimeInterval
    """

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default="walletobjects#timeInterval",
    )

    start: DateTime | None = None
    end: DateTime | None = None
