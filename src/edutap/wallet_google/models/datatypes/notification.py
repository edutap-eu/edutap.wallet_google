from ..bases import Model


# Attribute order as in Google's documentation to make future updates easier!
# Parity with the API is checked by tests/test_check_models.py


class ExpiryNotification(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/genericobject#expirynotification
    """

    enableNotification: bool = False


class UpcomingNotification(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/genericobject#upcomingnotification
    """

    enableNotification: bool = False


class Notifications(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/genericobject#notifications
    """

    expiryNotification: ExpiryNotification | None = None
    upcomingNotification: UpcomingNotification | None = None
