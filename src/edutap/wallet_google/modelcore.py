from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class GoogleWalletModel(BaseModel):
    """
    Base model for all Google Wallet models.
    """

    model_config = ConfigDict(
        extra="forbid",
        # extra="ignore",
        use_enum_values=True,
    )


class GoogleWalletWithKindModel(GoogleWalletModel):
    """
    Base model for Google Wallet models with an deprecated kind identifier.
    """

    kind: str | None = Field(description="deprecated", exclude=True, default=None)


class GoogleWalletWithIdModel(GoogleWalletWithKindModel):
    """
    Base model for Google Wallet models with an identifier.
    """

    # kind: str | None = Field(description="deprecated", exclude=True, default=None)
    id: str
