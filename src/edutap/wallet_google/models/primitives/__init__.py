from .enums import AnimationType
from .enums import NfcConstraint
from .enums import ScreenshotEligibility
from .localized_string import LocalizedString
from pydantic import AnyUrl
from pydantic import BaseModel
from pydantic import Field
from pydantic import HttpUrl


class Uri(BaseModel):
    uri: AnyUrl | str | None = None
    description: str | None = None
    localizedDescription: LocalizedString | None = None
    id: str | None = None


class ImageUri(BaseModel):
    uri: AnyUrl
    description: str | None = None
    localizedDescription: LocalizedString | None = None


class Image(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/Image
    """

    sourceUri: ImageUri
    contentDescription: LocalizedString | None = None


class PassConstraints(BaseModel):
    screenshotEligibility: ScreenshotEligibility = (
        ScreenshotEligibility.SCREENSHOT_ELIGIBILITY_UNSPECIFIED
    )
    nfcConstraint: list[NfcConstraint] | None = Field(
        default_factory=lambda: [
            NfcConstraint.NFC_CONSTRAINT_UNSPECIFIED,
        ]
    )


class SecurityAnimation(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/SecurityAnimation
    """

    animationType: AnimationType = AnimationType.ANIMATION_UNSPECIFIED


class GroupingInfo(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/GroupingInfo
    """

    sortIndex: int | None = None
    groupingId: str | None = None


class Pagination(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/Pagination
    """

    resultsPerPage: int
    nextPageToken: str | None = None


class CallbackOptions(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/CallbackOptions
    """

    url: HttpUrl | None = None
    updateRequestUrl: HttpUrl | None = None  # deprecated Attribute
