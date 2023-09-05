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

    expiryNotification: ExpiryNotification | None
    upcomingNotification: UpcomingNotification | None


class Message(BaseModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/Message
    """

    kind: str | None = "walletobjects#walletObjectMessage"
    header: str | None
    body: str | None
    displayInterval: TimeInterval | None
    id: str | None
    messageType: MessageType = MessageType.MESSAGE_TYPE_UNSPECIFIED
    locaizedHeader: LocalizedString | None
    localizedBody: LocalizedString | None


class AddMessageRequest(BaseModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/AddMessageRequest
    """

    message: Message
