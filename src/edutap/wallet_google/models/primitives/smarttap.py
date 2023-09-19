from .enums import Action
from .enums import Role
from pydantic import AnyHttpUrl
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import HttpUrl
from pydantic import Json


class Permission(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/permissions#permission
    """

    emailAddress: EmailStr | None
    role: Role | None


class AuthenticationKey(BaseModel):
    """
    see: https://developers.google.com/wallet/tickets/events/rest/v1/issuer#authenticationkey
    """

    id: int
    publicKeyPem: str


class SignUpInfo(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/smarttap#signupinfo
    """

    classId: str


class IssuerToUserInfo(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/smarttap#issuertouserinfo
    """

    action: Action = Action.ACTION_UNSPECIFIED
    url: AnyHttpUrl | None = None
    value: Json | None = None
    signUpInfo: SignUpInfo | None = None


class IssuerContactInfo(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/issuer#issuercontactinfo
    """

    name: str | None = None
    phone: str | None = None
    homepageUrl: HttpUrl | None = None
    email: EmailStr | None = None
    alertsEmails: list[EmailStr] | None = None


class SmartTapMerchantData(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/issuer#smarttapmerchantdata
    """

    smartTapMerchantId: str | None = None
    authenticationKeys: list[AuthenticationKey] | None = None
