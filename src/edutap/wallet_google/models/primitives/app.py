from . import Image
from . import LocalizedString
from . import Uri
from dataclasses import dataclass


@dataclass
class AppTarget:
    targetUri: Uri


@dataclass
class AppLinkInfo:
    appLogoImage: Image | None = None
    title: LocalizedString
    description: LocalizedString
    appTarget: AppTarget


@dataclass
class AppLinkData:
    androidAppLinkInfo: AppLinkInfo | None = None
    iosAppLinkInfo: AppLinkInfo | None = None
    webAppLinkInfo: AppLinkInfo | None = None
