from .._vendor.google_pay_token_decryption import GooglePayError
from .._vendor.google_pay_token_decryption import GooglePayTokenDecryptor
from ..models.callback import CallbackData
from ..settings import GoogleWalletSettings


def _raw_private_key(inkey: str) -> str:
    """
    Returns the raw private key.
    """
    result = ""
    for line in inkey.splitlines():
        if "BEGIN PRIVATE KEY" in line:
            continue
        if "END PRIVATE KEY" in line:
            break
        result += line.strip()
    return result


def verify_signature(data: CallbackData) -> bool:
    """
    Verifies the signature of the callback data.
    """
    settings = GoogleWalletSettings()
    decryptor = GooglePayTokenDecryptor(
        settings.google_root_signing_public_keys.dict()["keys"],
        settings.issuer_id,
        _raw_private_key(settings.credentials_info["private_key"]),
    )
    try:
        decryptor.verify_signature(dict(data))
    except GooglePayError:
        return False
    return True
