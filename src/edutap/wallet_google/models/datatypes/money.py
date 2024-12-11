from pydantic import BaseModel


class Money(BaseModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/Money
    """

    micros: str | None = None
    currencyCode: str | None = None
