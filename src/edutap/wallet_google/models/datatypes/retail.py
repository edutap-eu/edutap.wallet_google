from .enums import SharedDataType
from .enums import State
from .general import Uri
from pydantic import BaseModel


class DiscoverableProgramMerchantSignupInfo(BaseModel):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyclass#LoyaltyClass.DiscoverableProgramMerchantSigninInfo
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

    merchantSignupInfo: DiscoverableProgramMerchantSignupInfo | None = None
    merchantSigninInfo: DiscoverableProgramMerchantSigninInfo | None = None
    state: State = State.STATE_UNSPECIFIED
