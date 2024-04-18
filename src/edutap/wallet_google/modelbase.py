from pydantic import BaseModel
from pydantic import ConfigDict


class GoogleWalletModel(BaseModel):
    """
    Base model for all Google Wallet models.
    """

    model_config = ConfigDict(
        extra="forbid",
        use_enum_values=True,
    )


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
