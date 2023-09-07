from pydantic import BaseModel


class Review(BaseModel):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/Review
    """

    comments: str | None = None
