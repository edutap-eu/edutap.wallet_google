from .enums import AnimationType
from .enums import NfcConstraint
from .enums import ScreenshotEligibility
from .localized_string import LocalizedString
from pydantic import AnyUrl
from pydantic import BaseModel
from pydantic import Field
from pydantic import HttpUrl


class Uri(BaseModel):
    kind: str | None = "walletobjects#uri"
    uri: AnyUrl | str | None
    description: str | None
    localizedDescription: LocalizedString | None
    id: str | None


class ImageUri(BaseModel):
    uri: AnyUrl
    description: str | None
    localizedDescription: LocalizedString | None


class Image(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/Image
    """

    sourceUri: ImageUri
    contentDescription: LocalizedString | None
    kind: str | None = "walletobjects#image"


class PassConstraints(BaseModel):
    screenshotEligibility: ScreenshotEligibility = (
        ScreenshotEligibility.SCREENSHOT_ELIGIBILITY_UNSPECIFIED
    )
    nfcConstraint: list[NfcConstraint] | None = Field(
        default_factory=list(
            [
                NfcConstraint.NFC_CONSTRAINT_UNSPECIFIED,
            ]
        )
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

    sortIndex: int | None
    groupingId: str | None


class Pagination(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/Pagination
    """

    resultsPerPage: int
    nextPageToken: str | None
    kind: str | None = "walletobjects#pagination"


class CallbackOptions(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/CallbackOptions
    """

    url: HttpUrl | None
    updateRequestUrl: HttpUrl | None  # deprecated Attribute
