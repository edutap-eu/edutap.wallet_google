from ..bases import Model
from pydantic import Field


class TranslatedString(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/LocalizedString#translatedstring
    """

    language: str | None = Field(default=None)
    value: str | None = Field(default=None)


class LocalizedString(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/LocalizedString
    """

    defaultValue: TranslatedString
    translatedValues: list[TranslatedString] = Field(default=[])
