from . import Image
from . import Uri
from .localized_string import LocalizedString
from pydantic import BaseModel


class TextModuleData(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/TextModuleData
    """

    header: str | None
    body: str | None
    localizedHeader: LocalizedString | None
    localizedBody: LocalizedString | None
    id: str | None


class LabelValue(BaseModel):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/InfoModuleData#labelvalue
    """

    label: str | None
    value: str | None
    localizedLabel: LocalizedString | None
    localizedValue: LocalizedString | None


class LabelValueRow(BaseModel):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/InfoModuleData#labelvaluerow
    """

    columns: list[LabelValue] | None


class LinksModuleData(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/LinksModuleData
    """

    uris: list[Uri] | None


class ImageModuleData(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ImageModuleData
    """

    mainImage: Image | None
    id: str | None


class InfoModuleData(BaseModel):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/InfoModuleData
    """

    labelValueRows: list[LabelValueRow]
    showLastUpdatedTime: bool | None = False  # deprecated


class AppTarget(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/AppLinkData#apptargets
    """

    targetUri: Uri | None


class AppLinkInfo(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/AppLinkData#applinkinfo
    """

    appLogoImage: Image | None
    title: LocalizedString | None
    description: LocalizedString | None
    appTarget: AppTarget | None


class AppLinkData(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/AppLinkData
    """

    androidAppLinkInfo: AppLinkInfo | None
    iosAppLinkInfo: AppLinkInfo | None
    webAppLinkInfo: AppLinkInfo | None
