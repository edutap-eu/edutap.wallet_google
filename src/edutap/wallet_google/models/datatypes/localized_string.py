from pydantic import BaseModel
from pydantic import Field


class TranslatedString(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/LocalizedString#translatedstring
    """

    language: str | None = Field(default=None)
    value: str | None = Field(default=None)


class LocalizedString(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/LocalizedString
    """

    defaultValue: TranslatedString
    translatedValues: list[TranslatedString] = Field(default=[])
