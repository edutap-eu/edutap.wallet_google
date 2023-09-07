from pydantic import BaseModel
from pydantic import Field


class TranslatedString(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/LocalizedString#translatedstring
    """

    language: str | None = Field(kwarg_only=False, default=None)
    value: str | None = Field(kwarg_only=False, default=None)


class LocalizedString(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/LocalizedString
    """

    defaultValue: TranslatedString = Field(kwarg_only=False)
    translatedValues: list[TranslatedString] = Field(kwarg_only=False, default=[])
