from ..bases import Model


class Review(Model):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/Review
    """

    comments: str | None = None
