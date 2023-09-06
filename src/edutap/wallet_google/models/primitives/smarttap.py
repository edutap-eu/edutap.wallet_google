from .enums import Action
from pydantic import AnyHttpUrl
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import HttpUrl
from pydantic import Json


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

    action: Action | None = Action.ACTION_UNSPECIFIED
    url: AnyHttpUrl | None
    value: Json | None
    signUpInfo: SignUpInfo | None


class SmartTap(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/smarttap#resource:-smarttap
    """

    kind: str | None = "walletobjects#smartTap"
    id: str
    merchantId: str
    infos: list[IssuerToUserInfo] | None


class IssuerContactInfo(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/issuer#issuercontactinfo
    """

    name: str | None
    phone: str | None
    homepageUrl: HttpUrl | None
    email: EmailStr | None
    alertsEmails: list[EmailStr] | None


class SmartTapMerchantData(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/issuer#smarttapmerchantdata
    """

    smartTapMerchantId: str | None
    authenticationKeys: list[AuthenticationKey] | None
