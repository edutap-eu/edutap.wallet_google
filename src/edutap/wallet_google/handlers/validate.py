from .._vendor.google_pay_token_decryption import GooglePayError
from .._vendor.google_pay_token_decryption import GooglePayTokenDecryptor
from ..models.callback import CallbackData
from ..settings import GoogleWalletSettings


def verify_signature(data: CallbackData) -> bool:
    """
    Verifies the signature of the callback data.
    """
    settings = GoogleWalletSettings()
    decryptor = GooglePayTokenDecryptor(
        settings.google_root_signing_public_keys.dict()["keys"],
        settings.credentials_info["issuer_id"],
        settings.credentials_info["private_key"],
    )
    try:
        decryptor.verify_signature(dict(data))
    except GooglePayError:
        return False
    return True
