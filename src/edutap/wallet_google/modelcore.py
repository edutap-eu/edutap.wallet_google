from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class GoogleWalletModel(BaseModel):
    """
    Base Model for all Google Wallet Models.

    Sets a model_config for all Google Wallet Models that enforce that all attributes must be explicitly modeled, and trying to set an unknown attribute would raise an Exception.
    This Follows the Zen of Python (PEP 20) --> Explicit is better than implicit.
    """

    model_config = ConfigDict(
        extra="forbid",
        # extra="ignore",
        # use_enum_values=True,
    )


class GoogleWalletWithKindMixin(BaseModel):
    """
    Mixin Class for Google Wallet Models with an deprecated kind identifier.
    Explicit kind value should be provided by the inheriting concret class.
    """

    kind: str | None = Field(
        description="deprecated",
        deprecated=True,
        exclude=True,
        default=None,
    )


class GoogleWalletWithIdModel(BaseModel):
    """
    Model for Google Wallet models with an identifier.
    """

    id: str
