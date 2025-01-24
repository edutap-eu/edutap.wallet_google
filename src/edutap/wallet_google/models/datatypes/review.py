from ..bases import Model


# Attribute order as in Google's documentation to make future updates easier!
# last check: 2025-01-22


class Review(Model):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/Review
    """

    comments: str | None = None
