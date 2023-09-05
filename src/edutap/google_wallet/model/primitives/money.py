from pydantic import BaseModel


class Money(BaseModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/Money
    """

    kind: str | None = "walletobjects#money"
    micros: str | None
    currencyCode: str | None
