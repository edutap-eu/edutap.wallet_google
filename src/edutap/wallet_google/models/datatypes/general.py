from ..bases import Model
from ..deprecated import DeprecatedKindFieldMixin
from .enums import AnimationType
from .enums import NfcConstraint
from .enums import ScreenshotEligibility
from .localized_string import LocalizedString
from pydantic import AnyUrl
from pydantic import Field
from pydantic import HttpUrl
from typing import Annotated
from typing_extensions import deprecated


# Attribute order as in Google's documentation to make future updates easier!
# last check: 2025-01-22


class Uri(DeprecatedKindFieldMixin, Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/Uri
    """

    # inherits kind (deprecated)
    uri: AnyUrl | str | None = None
    description: str | None = None
    localizedDescription: LocalizedString | None = None
    id: str | None = None


class ImageUri(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/Image#imageuri
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
    """

    # inherits kind (deprecated)
    sourceUri: ImageUri
    contentDescription: LocalizedString | None = None


class PassConstraints(Model):
    """
    see https://developers.google.com/wallet/generic/rest/v1/PassConstraints
    """

    screenshotEligibility: ScreenshotEligibility = (
        ScreenshotEligibility.SCREENSHOT_ELIGIBILITY_UNSPECIFIED
    )
    nfcConstraint: list[NfcConstraint] | None = Field(
        default_factory=lambda: [
            NfcConstraint.NFC_CONSTRAINT_UNSPECIFIED,
        ]
    )


class SecurityAnimation(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/SecurityAnimation
    """

    animationType: AnimationType = AnimationType.ANIMATION_UNSPECIFIED


class GroupingInfo(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/GroupingInfo
    """

    sortIndex: int | None = None
    groupingId: str | None = None


class Pagination(DeprecatedKindFieldMixin, Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/Pagination
    """

    # inherits kind (deprecated)
    resultsPerPage: int
    nextPageToken: str | None = None


class CallbackOptions(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/CallbackOptions
    """

    url: HttpUrl | None = None
    updateRequestUrl: Annotated[
        HttpUrl | None,
        Field(
            deprecated=deprecated(
                'The Parameter "updateRequestUrl" is deprecated on "CallbackOption", use "url" instead.'
            ),
            default=None,
            exclude=True,
        ),
    ]


class SaveRestrictions(Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/SaveRestrictions
    """

    restrictToEmailSha256: str | None = None
