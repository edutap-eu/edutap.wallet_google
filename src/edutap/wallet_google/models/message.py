from .bases import Model
from .datatypes.message import Message


class AddMessageRequest(Model):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/AddMessageRequest
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    message: Message | None = None
