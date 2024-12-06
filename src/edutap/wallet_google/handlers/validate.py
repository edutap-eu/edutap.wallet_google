from .._vendor.google_pay_token_decryption import GooglePayTokenDecryptor
from ..models.callback import CallbackData
from ..settings import GoogleWalletSettings


def verify_signature(data: CallbackData) -> bool:
    """
    Verifies the signature of the callback data.
    """
    # TODO
    settings = GoogleWalletSettings()
    decryptor = GooglePayTokenDecryptor(
        settings.credentials_file,
        settings.issuer_account_email,
        settings.issuer_id,
    )
    decryptor.decrypt(data)
    return True
