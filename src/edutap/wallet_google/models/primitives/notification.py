from .datetime import TimeInterval
from .enums import MessageType
from .localized_string import LocalizedString
from pydantic import BaseModel


class ExpiryNotification(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/genericobject#expirynotification
    """

    enableNotification: bool = False


class UpcomingNotification(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/genericobject#upcomingnotification
    """

    enableNotification: bool = False


class Notifications(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/genericobject#notifications
    """

    expiryNotification: ExpiryNotification | None = None
    upcomingNotification: UpcomingNotification | None = None


class Message(BaseModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/Message
    """

    header: str | None = None
    body: str | None = None
    displayInterval: TimeInterval | None = None
    id: str | None = None
    messageType: MessageType = MessageType.MESSAGE_TYPE_UNSPECIFIED
    localizedHeader: LocalizedString | None = None
    localizedBody: LocalizedString | None = None


class AddMessageRequest(BaseModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/AddMessageRequest
    """

    message: Message
