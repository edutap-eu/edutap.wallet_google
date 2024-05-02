from ...modelcore import GoogleWalletModel
from ...modelcore import GoogleWalletWithKindMixin
from .datetime import TimeInterval
from .enums import MessageType
from .localized_string import LocalizedString
from pydantic import Field


class Message(
    GoogleWalletModel,
    GoogleWalletWithKindMixin,
):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/Message
    """

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default="walletobjects#walletObjectMessage",
    )
    id: str | None = None
    messageType: MessageType = MessageType.MESSAGE_TYPE_UNSPECIFIED
    displayInterval: TimeInterval | None = None
    header: str | None = None
    localizedHeader: LocalizedString | None = None
    body: str | None = None
    localizedBody: LocalizedString | None = None


class AddMessageRequest(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/AddMessageRequest
    """

    message: Message | None = None
