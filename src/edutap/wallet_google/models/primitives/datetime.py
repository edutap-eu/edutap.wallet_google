from ...modelcore import GoogleWalletModel
from ...modelcore import GoogleWalletWithKindMixin
from pydantic import Field

import datetime


class DateTime(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/DateTime
    """

    date: datetime.datetime


class TimeInterval(GoogleWalletModel, GoogleWalletWithKindMixin):
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
