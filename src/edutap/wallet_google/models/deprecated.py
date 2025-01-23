"""
Many Google wallet models or datatypes have deprecated attributes.
Those must not be serialized again, nor repeated in the special models.
To handle this, we create mixins which can be added to the models which still have the deprecated fields.
"""

from edutap.wallet_google.models.datatypes.data import InfoModuleData
from edutap.wallet_google.models.datatypes.general import Image
from edutap.wallet_google.models.datatypes.location import LatLongPoint
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
            # TODO: should this be set to False? or rather None?
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
