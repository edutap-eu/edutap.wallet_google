from ..registry import register_model
from .bases import Model
from .bases import WithIdModel
from .datatypes.general import CallbackOptions
from .datatypes.smarttap import IssuerContactInfo
from .datatypes.smarttap import IssuerToUserInfo
from .datatypes.smarttap import Permission
from .datatypes.smarttap import SmartTapMerchantData


@register_model(
    "SmartTap",
    url_part="smartTap",
    can_read=False,
    can_update=False,
    can_disable=False,
    can_list=False,
    can_message=False,
)
class SmartTap(WithIdModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/smarttap#resource:-smarttap
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    # inherits id
    merchantId: str
    infos: list[IssuerToUserInfo] | None = None


@register_model(
    "Issuer",
    url_part="issuer",
    resource_id="issuerId",
    can_message=False,
)
class Issuer(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/issuer
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    issuerId: str
    name: str
    contactInfo: IssuerContactInfo | None = None
    homepageUrl: str | None = None
    smartTapMerchantData: SmartTapMerchantData | None = None
    callbackOptions: CallbackOptions | None = None


@register_model(
    "Permissions",
    url_part="permissions",
    resource_id="issuerId",
    can_disable=False,
    can_list=False,
    can_message=False,
)
class Permissions(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/permissions
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-11-29

    issuerId: str | None = None
    permissions: list[Permission] = []
