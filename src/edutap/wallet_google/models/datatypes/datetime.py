from ..bases import Model
from ..deprecated import DeprecatedKindFieldMixin

# TODO: imports itself, i.e. shadows the datetime module
import datetime


# Attribute order as in Google's documentation to make future updates easier!
# last check: 2025-01-22


class DateTime(Model):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/DateTime
    """

    date: datetime.datetime


class TimeInterval(DeprecatedKindFieldMixin, Model):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/TimeInterval
    """

    # inherits kind (deprecated)
    start: DateTime | None = None
    end: DateTime | None = None
