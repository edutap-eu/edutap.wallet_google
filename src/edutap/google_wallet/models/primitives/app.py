from . import Image
from . import LocalizedString
from . import Uri
from dataclasses import dataclass


@dataclass
class AppTarget:
    targetUri: Uri


@dataclass
class AppLinkInfo:
    appLogoImage: Image | None
    title: LocalizedString
    description: LocalizedString
    appTarget: AppTarget


@dataclass
class AppLinkData:
    androidAppLinkInfo: AppLinkInfo | None
    iosAppLinkInfo: AppLinkInfo | None
    webAppLinkInfo: AppLinkInfo | None
