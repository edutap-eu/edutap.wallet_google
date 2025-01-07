from ..bases import Model
from .general import Image
from .general import Uri
from .localized_string import LocalizedString
from pydantic import Field


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
    showLastUpdatedTime: bool = Field(
        description="deprecated",
        exclude=True,
        default=False,
    )


class AppTarget(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/AppLinkData#apptargets
    """

    targetUri: Uri | None = None


class AppLinkInfo(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/AppLinkData#applinkinfo
    """

    appLogoImage: Image | None = None
    title: LocalizedString | None = None
    description: LocalizedString | None = None
    appTarget: AppTarget | None = None


class AppLinkData(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/AppLinkData
    """

    androidAppLinkInfo: AppLinkInfo | None = None
    iosAppLinkInfo: AppLinkInfo | None = None
    webAppLinkInfo: AppLinkInfo | None = None
