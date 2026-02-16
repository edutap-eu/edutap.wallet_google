from ..bases import Model
from .enums import Action
from .enums import Role
from pydantic import AnyHttpUrl
from pydantic import EmailStr
from pydantic import Field


# Attribute order as in Google's documentation to make future updates easier!
# last check: 2025-01-22


class Permission(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/permissions#permission
    """

    emailAddress: EmailStr | None
    role: Role | None


class AuthenticationKey(Model):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/issuer#authenticationkey
    """

    id: int
    publicKeyPem: str


class SignUpInfo(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/smarttap#signupinfo
    """

    classId: str


class IssuerToUserInfo(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/smarttap#issuertouserinfo
    """

    action: Action = Action.ACTION_UNSPECIFIED
    url: AnyHttpUrl | None = Field(
        description="Currently not used, consider deprecating", default=None
    )
    value: str | None = None
    signUpInfo: SignUpInfo | None = None


class IssuerContactInfo(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/issuer#issuercontactinfo
    """

    name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    alertsEmails: list[EmailStr] | None = None


class SmartTapMerchantData(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/issuer#smarttapmerchantdata
    """

    smartTapMerchantId: str | None = None
    authenticationKeys: list[AuthenticationKey] | None = None
