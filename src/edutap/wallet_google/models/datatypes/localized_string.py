from ..bases import Model
from ..deprecated import DeprecatedKindFieldMixin
from pydantic import Field


# Attribute order as in Google's documentation to make future updates easier!
# last check: 2025-01-22


class TranslatedString(DeprecatedKindFieldMixin, Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/LocalizedString#translatedstring
    """

    # inherits kind (deprecated)
    language: str | None = Field(default=None)
    value: str | None = Field(default=None)


class LocalizedString(DeprecatedKindFieldMixin, Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/LocalizedString
    """

    # inherits kind (deprecated)
    translatedValues: list[TranslatedString] = Field(default_factory=list)
    defaultValue: TranslatedString
