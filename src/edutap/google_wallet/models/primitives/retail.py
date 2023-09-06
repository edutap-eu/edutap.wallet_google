from . import Uri
from .enums import SharedDataType
from .enums import State
from pydantic import BaseModel


class DiscoverableProgramMerchantSignupInfo(BaseModel):
    """
    see:
    """

    signupWebsite: Uri
    signupSharedDatas: list[SharedDataType]


class DiscoverableProgramMerchantSigninInfo(BaseModel):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyclass#discoverableprogrammerchantsignininfo
    """

    signinWebsite: Uri


class DiscoverableProgram(BaseModel):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyclass#discoverableprogram
    """

    merchantSignupInfo: DiscoverableProgramMerchantSignupInfo | None
    merchantSigninInfo: DiscoverableProgramMerchantSigninInfo | None
    state: State | None = State.STATE_UNSPECIFIED
