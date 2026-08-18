from ..bases import Model


# Attribute order as in Google's documentation to make future updates easier!
# Parity with the API is checked by tests/test_check_models.py


class Review(Model):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/Review
    """

    comments: str | None = None
