from ..bases import Model
from .enums import AnimationType
from .enums import NfcConstraint
from .enums import ScreenshotEligibility
from .localized_string import LocalizedString
from pydantic import AnyUrl
from pydantic import Field
from pydantic import HttpUrl


class Uri(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/Uri
    """

    uri: AnyUrl | str | None = None
    description: str | None = None
    localizedDescription: LocalizedString | None = None
    id: str | None = None


class ImageUri(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/Image#imageuri
    """

    uri: AnyUrl
    description: str | None = Field(deprecated=True, default=None, exclude=True)
    localizedDescription: LocalizedString | None = Field(
        deprecated=True, default=None, exclude=True
    )


class Image(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/Image
    """

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


class Pagination(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/Pagination
    """

    resultsPerPage: int
    nextPageToken: str | None = None


class CallbackOptions(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/CallbackOptions
    """

    url: HttpUrl | None = None


class SaveRestrictions(Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/SaveRestrictions
    """

    restrictToEmailSha256: str | None = None
