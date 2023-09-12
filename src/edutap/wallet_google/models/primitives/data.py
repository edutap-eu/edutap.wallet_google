from . import Image
from . import Uri
from .localized_string import LocalizedString
from pydantic import BaseModel
from pydantic import Field


class TextModuleData(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/TextModuleData
    """

    header: str | None = None
    body: str | None = None
    localizedHeader: LocalizedString | None = None
    localizedBody: LocalizedString | None = None
    id: str | None = None


class LabelValue(BaseModel):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/InfoModuleData#labelvalue
    """

    label: str | None = None
    value: str | None = None
    localizedLabel: LocalizedString | None = None
    localizedValue: LocalizedString | None = None


class LabelValueRow(BaseModel):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/InfoModuleData#labelvaluerow
    """

    columns: list[LabelValue] | None = None


class LinksModuleData(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/LinksModuleData
    """

    uris: list[Uri] | None = None


class ImageModuleData(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ImageModuleData
    """

    mainImage: Image | None = None
    id: str | None = None


class InfoModuleData(BaseModel):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/InfoModuleData
    """

    labelValueRows: list[LabelValueRow]
    showLastUpdatedTime: bool = Field(
        description="deprecated",
        exclude=True,
        default=False,
    )


class AppTarget(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/AppLinkData#apptargets
    """

    targetUri: Uri | None = None


class AppLinkInfo(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/AppLinkData#applinkinfo
    """

    appLogoImage: Image | None = None
    title: LocalizedString | None = None
    description: LocalizedString | None = None
    appTarget: AppTarget | None = None


class AppLinkData(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/AppLinkData
    """

    androidAppLinkInfo: AppLinkInfo | None = None
    iosAppLinkInfo: AppLinkInfo | None = None
    webAppLinkInfo: AppLinkInfo | None = None
