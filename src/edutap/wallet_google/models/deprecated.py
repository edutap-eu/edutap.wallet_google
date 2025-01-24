"""
Many Google wallet models or datatypes have deprecated attributes.
Those must not be serialized again, nor repeated in the special models.
To handle this, we create mixins which can be added to the models which still have the deprecated fields.
"""

from .bases import Model
from pydantic import AnyUrl
from pydantic import Field
from typing import Annotated
from typing_extensions import deprecated


class DeprecatedKindFieldMixin:
    """
    Mixin to add the deprecated kind field to a model.
    May be removed in the future.
    """

    kind: Annotated[
        str,
        Field(
            deprecated=deprecated(
                'Attribute "kind" was used in the past to identify resources but is now deprecated.'
            ),
            exclude=True,
            default=None,
        ),
    ]


class DeprecatedAllowMultipleUsersPerObjectMixin:
    """
    Mixin to add the deprecated allowMultipleUsersPerObject field to a model.
    May be removed in the future.
    """

    allowMultipleUsersPerObject: Annotated[
        bool,
        Field(
            deprecated=deprecated(
                'Attribute "allowMultipleUsersPerObject" was used in the past to allow multiple users per object but is now deprecated.'
            ),
            exclude=True,
            default=False,
        ),
    ]


class DeprecatedVersionFieldMixin:
    """
    Mixin to add the deprecated version field to a model.
    May be removed in the future.
    """

    version: Annotated[
        str | None,
        Field(
            deprecated=deprecated(
                'Attribute "version" was used in the past to specify the version of the resource but is now deprecated.'
            ),
            exclude=True,
            default=None,
        ),
    ]


class LatLongPoint(DeprecatedKindFieldMixin, Model):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/LatLongPoint

    To avoid circular imports this model is a duplicate of the one in location.py

    Deprecated!
    """

    # inherits kind (deprecated)
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)


class DeprecatedLocationsFieldMixin:
    """
    Mixin to add the deprecated locations field to a model.
    May be removed in the future.
    """

    locations: Annotated[
        LatLongPoint | None,
        Field(
            deprecated=deprecated(
                'Attribute "locations" was used in the past to specify locations but is now deprecated.'
            ),
            exclude=True,
            default=None,
        ),
    ]


class TranslatedString(DeprecatedKindFieldMixin, Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/LocalizedString#translatedstring

    To avoid circular imports this model is a duplicate of the one in location.py

    Deprecated!
    """

    # inherits kind (deprecated)
    language: str | None = Field(default=None)
    value: str | None = Field(default=None)


class LocalizedString(DeprecatedKindFieldMixin, Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/LocalizedString

    To avoid circular imports this model is a duplicate of the one in localized_string.py

    Deprecated!
    """

    # inherits kind (deprecated)
    translatedValues: list[TranslatedString] = Field(default_factory=list)
    defaultValue: TranslatedString


class LabelValue(Model):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/InfoModuleData#labelvalue

    To avoid circular imports this model is a duplicate of the one in data.py

    Deprecated!
    """

    label: str | None = None
    value: str | None = None
    localizedLabel: LocalizedString | None = None
    localizedValue: LocalizedString | None = None


class LabelValueRow(Model):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/InfoModuleData#labelvaluerow

    To avoid circular imports this model is a duplicate of the one in data.py

    Deprecated!
    """

    columns: list[LabelValue] | None = None


class InfoModuleData(Model):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/InfoModuleData

    To avoid circular imports this model is a duplicate of the one in data.py

    Deprecated!
    """

    labelValueRows: list[LabelValueRow]
    showLastUpdateTime: Annotated[
        bool,
        Field(
            deprecated=deprecated(
                'The Attribute "showLastUpdateTime" on "InfoModuleData" is deprecated.'
            ),
            exclude=True,
            default=False,
        ),
    ]


class DeprecatedInfoModuleDataFieldMixin:
    """
    Mixin to add the deprecated infoModuleData field to a model.
    May be removed in the future.
    """

    infoModuleData: Annotated[
        InfoModuleData | None,
        Field(
            deprecated=deprecated(
                'Attribute "infoModuleData" was used in the past to specify info module data but is now deprecated.'
            ),
            exclude=True,
            default=None,
        ),
    ]


class ImageUri(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/Image#imageuri

    To avoid circular imports this model is a duplicate of the one in general.py

    Deprecated!
    """

    uri: AnyUrl
    description: Annotated[
        str | None,
        Field(
            deprecated=deprecated(
                'The Attribute "description" is deprecated on "ImageUri", use "contentDesceription" on parent "Image" Instance.'
            ),
            default=None,
            exclude=True,
        ),
    ]
    localizedDescription: Annotated[
        LocalizedString | None,
        Field(
            deprecated=deprecated(
                'The Attribute "localizedDescription" is deprecated on "ImageUri", use "contentDesceription" on parent "Image" Instance.'
            ),
            default=None,
            exclude=True,
        ),
    ]


class Image(DeprecatedKindFieldMixin, Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/Image

    To avoid circular imports this model is a duplicate of the one in general.py

    Deprecated!
    """

    # inherits kind (deprecated)
    sourceUri: ImageUri
    contentDescription: LocalizedString | None = None


class DeprecatedWordMarkFieldMixin:
    """
    Mixin to add the deprecated wordMark field to a model.
    May be removed in the future.
    """

    wordMark: Annotated[
        list[Image] | None,
        Field(
            deprecated=deprecated(
                'Attribute "wordMark" was used in the past to specify the word mark but is now deprecated.'
            ),
            exclude=True,
            default=None,
        ),
    ]
