from ..bases import Model
from ..deprecated import DeprecatedKindFieldMixin
from .datetime import TimeInterval
from .enums import MessageType
from .localized_string import LocalizedString


# Attribute order as in Google's documentation to make future updates easier!
# last check: 2025-01-22


class Message(DeprecatedKindFieldMixin, Model):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/Message
    """

    # inherits kind (deprecated)
    header: str | None = None
    body: str | None = None
    displayInterval: TimeInterval | None = None
    id: str | None = None
    messageType: MessageType = MessageType.MESSAGE_TYPE_UNSPECIFIED
    localizedHeader: LocalizedString | None = None
    localizedBody: LocalizedString | None = None
