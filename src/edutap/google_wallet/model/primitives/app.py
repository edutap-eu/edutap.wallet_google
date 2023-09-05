from . import Image
from . import LocalizedString
from . import Uri
from dataclasses import dataclass
from typing import Optional


@dataclass
class AppTarget:
    targetUri: Uri


@dataclass
class AppLinkInfo:
    appLogoImage: Optional[Image]
    title: LocalizedString
    description: LocalizedString
    appTarget: AppTarget


@dataclass
class AppLinkData:
    androidAppLinkInfo: Optional[AppLinkInfo]
    iosAppLinkInfo: Optional[AppLinkInfo]
    webAppLinkInfo: Optional[AppLinkInfo]
