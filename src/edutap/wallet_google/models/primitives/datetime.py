from ...modelcore import GoogleWalletModel

import datetime


class DateTime(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/DateTime
    """

    date: datetime.datetime


class TimeInterval(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/TimeInterval
    """

    start: DateTime | None = None
    end: DateTime | None = None
