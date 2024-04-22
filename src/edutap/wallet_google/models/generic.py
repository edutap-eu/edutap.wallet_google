from ..modelbase import GoogleWalletClassModel
from ..modelbase import GoogleWalletObjectModel
from ..registry import register_model
from .primitives.data import AppLinkData
from .primitives.datetime import TimeInterval
from .primitives.enums import GenericType
from .primitives.enums import State
from .primitives.localized_string import LocalizedString
from .primitives.notification import Notifications
from pydantic import Field


@register_model(
    "GenericClass", url_part="genericClass", plural="genericClasses", can_disable=False
)
class GenericClass(GoogleWalletClassModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/genericclass
    """


@register_model("GenericObject", url_part="genericObject")
class GenericObject(GoogleWalletObjectModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/genericobject
    """

    genericType: GenericType = GenericType.GENERIC_TYPE_UNSPECIFIED
    cardTitle: LocalizedString | None = None
    subheader: LocalizedString | None = None
    header: LocalizedString | None = None
    notifications: Notifications | None = None
    validTimeInterval: TimeInterval | None = None
    appLinkData: AppLinkData | None = None
    state: State = Field(default=State.STATE_UNSPECIFIED)
    hasUsers: bool | None = None
