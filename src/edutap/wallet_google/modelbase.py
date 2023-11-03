from pydantic import BaseModel


class GoogleWalletModel(BaseModel):
    """
    Base model for all Google Wallet models.
    """


class GoogleWalletWithIdModel(GoogleWalletModel):
    """
    Base model for Google Wallet models with an identifier.
    """

    id: str


class GoogleWalletClassModel(GoogleWalletWithIdModel):
    """
    Base model for all Google Wallet Class models.
    """


class GoogleWalletObjectModel(GoogleWalletWithIdModel):
    """
    Base model for all Google Wallet Object models.
    """

    classId: str


class GoogleWalletObjectReference(GoogleWalletWithIdModel):
    """
    Model for all Google Wallet Object references.
    """

    classId: str | None = None
