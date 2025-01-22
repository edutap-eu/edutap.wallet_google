from ..bases import Model
from .general import Image
from .general import Uri
from .localized_string import LocalizedString
from pydantic import Field
from typing import Annotated
from typing_extensions import deprecated


# Attribute order as in Google's documentation to make future updates easier!
# last check: 2025-01-22


class TextModuleData(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/TextModuleData

    Google accepts both header and localizedHeader, body and localizedBody
    but if localizedHeader and localizedBody are present, header and body are ignored and set to None.
    """

    header: str | None = Field(max_length=35, default=None)
    body: str | None = Field(max_length=500, default=None)
    localizedHeader: LocalizedString | None = None
    localizedBody: LocalizedString | None = None
    id: str | None = None
    # TODO: custom field validator for id with Field(pattern="^[a-zA-Z0-9_-]+$") plus None


class LabelValue(Model):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/InfoModuleData#labelvalue
    """

    label: str | None = None
    value: str | None = None
    localizedLabel: LocalizedString | None = None
    localizedValue: LocalizedString | None = None


class LabelValueRow(Model):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/InfoModuleData#labelvaluerow
    """

    columns: list[LabelValue] | None = None


class LinksModuleData(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/LinksModuleData
    """

    uris: list[Uri] | None = None


class ImageModuleData(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ImageModuleData
    """

    mainImage: Image | None = None
    id: str | None = None


class InfoModuleData(Model):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/InfoModuleData
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


class AppTarget(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/AppLinkData#apptarget
    """

    targetUri: Uri | None = None
    packageName: str | None = None


class AppLinkInfo(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/AppLinkData#applinkinfo
    """

    #  TODO: add deprecated decorator to appLogoImage, title, description
    appLogoImage: Annotated[
        Image | None,
        Field(
            deprecated=deprecated(
                'The Attribute "appLogoImage" on "AppLinkInfo" is deprecated. Image isn\'t supported in the app link module'
            ),
            exclude=True,
            default=None,
        ),
    ]
    title: Annotated[
        LocalizedString | None,
        Field(
            deprecated=deprecated(
                'The Attribute "title" on "AppLinkInfo" is deprecated. Title isn\'t supported in the app link module'
            ),
            exclude=True,
            default=None,
        ),
    ]
    description: Annotated[
        LocalizedString | None,
        Field(
            deprecated=deprecated(
                'The Attribute "description" on "AppLinkInfo" is deprecated. Description isn\'t supported in the app link module'
            ),
            exclude=True,
            default=None,
        ),
    ]
    appTarget: AppTarget | None = None


class AppLinkData(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/AppLinkData
    """

    androidAppLinkInfo: AppLinkInfo | None = None
    iosAppLinkInfo: Annotated[
        AppLinkInfo | None,
        Field(
            deprecated=deprecated(
                'The Attribute "iosAppLinkInfo" on "AppLinkData" is deprecated. Links to open iOS apps are not supported'
            ),
            exclude=True,
            default=None,
        ),
    ]
    webAppLinkInfo: AppLinkInfo | None = None
    displayText: LocalizedString | None = None
