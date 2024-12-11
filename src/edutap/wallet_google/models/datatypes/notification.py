from ..bases import Model


class ExpiryNotification(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/genericobject#expirynotification
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

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

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    expiryNotification: ExpiryNotification | None = None
    upcomingNotification: UpcomingNotification | None = None
