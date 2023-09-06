from pydantic import BaseModel


class TranslatedString(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/LocalizedString#translatedstring
    """

    kind: str | None = "walletobjects#translatedString"
    language: str | None
    value: str | None


class LocalizedString(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/LocalizedString
    """

    kind: str | None = "walletobjects#localizedString"
    translatedValues: list[TranslatedString] | None
    defaultValue: TranslatedString
