from pydantic import BaseModel


class GoogleWalletModel(BaseModel):
    """
    Base model for all Google Wallet models.
    """

    id: str


class GoogleWalletClassModel(GoogleWalletModel):
    """
    Base model for all Google Wallet Class models.
    """


class GoogleWalletObjectModel(GoogleWalletModel):
    """
    Base model for all Google Wallet Object models.
    """

    classId: str


class GoogleWalletObjectReference(GoogleWalletObjectModel):
    """
    Model for all Google Wallet Object references.
    """

    classId: str | None = None
