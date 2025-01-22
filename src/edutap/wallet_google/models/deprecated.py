from pydantic import Field
from typing import Annotated
from typing_extensions import deprecated


"""
Many Google wallet models or datatypes have deprecated attributes.
Those must not be serialized again, nor repeated in the special models.
To handle this, we create mixins which can be added to the models which still have the deprecated fields.
"""


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
        str,
        Field(
            deprecated=deprecated(
                'Attribute "version" was used in the past to specify the version of the resource but is now deprecated.'
            ),
            exclude=True,
            default=None,
        ),
    ]
