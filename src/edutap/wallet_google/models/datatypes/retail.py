from ..bases import Model
from .enums import RetailState
from .enums import SharedDataType
from .general import Uri


# Attribute order as in Google's documentation to make future updates easier!
# last check: 2025-01-22


class DiscoverableProgramMerchantSignupInfo(Model):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyclass#discoverableprogrammerchantsignupinfo
    """

    signupWebsite: Uri
    signupSharedDatas: list[SharedDataType]


class DiscoverableProgramMerchantSigninInfo(Model):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyclass#discoverableprogrammerchantsignininfo
    """

    signinWebsite: Uri


class DiscoverableProgram(Model):
    """
    see: https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyclass#discoverableprogram
    """

    merchantSignupInfo: DiscoverableProgramMerchantSignupInfo | None = None
    merchantSigninInfo: DiscoverableProgramMerchantSigninInfo | None = None
    state: RetailState = RetailState.STATE_UNSPECIFIED
