from ..modelbase import GoogleWalletModel
from ..modelbase import GoogleWalletWithIdModel
from ..registry import register_model
from .primitives.smarttap import IssuerContactInfo
from .primitives.smarttap import IssuerToUserInfo
from .primitives.smarttap import Permission
from .primitives.smarttap import SmartTapMerchantData


@register_model(
    "SmartTap",
    url_part="smartTap",
    can_read=False,
    can_update=False,
    can_disable=False,
    can_list=False,
    can_message=False,
)
class SmartTap(GoogleWalletWithIdModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/smarttap#resource:-smarttap
    """

    merchantId: str
    infos: list[IssuerToUserInfo] | None = None


@register_model(
    "Issuer",
    url_part="issuer",
    resource_id="issuerId",
    can_message=False,
)
class Issuer(GoogleWalletModel):
    issuerId: str
    name: str
    contactInfo: IssuerContactInfo | None
    homepageUrl: str | None
    smartTapMerchantData: SmartTapMerchantData | None


@register_model(
    "Permissions",
    url_part="permissions",
    resource_id="issuerId",
    can_disable=False,
    can_list=False,
    can_message=False,
)
class Permissions(GoogleWalletModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/permissions
    """

    issuerId: str | None
    permissions: list[Permission]
