from .._vendor.google_pay_token_decryption import GooglePayTokenDecryptor
from ..models.callback import CallbackData
from ..models.callback import SignedMessage
from ..settings import GoogleWalletSettings


def _raw_private_key(in_key: str) -> str:
    """
    Returns the raw private key.
    """
    result = ""
    for line in in_key.splitlines():
        if "BEGIN PRIVATE KEY" in line:
            continue
        if "END PRIVATE KEY" in line:
            break
        result += line.strip()
    return result


def verified_signed_message(data: CallbackData) -> SignedMessage:
    """
    Verifies the signature of the callback data.
    and returns the parsed SignedMessage
    """
    settings = GoogleWalletSettings()
    decryptor = GooglePayTokenDecryptor(
        settings.google_root_signing_public_keys.dict()["keys"],
        settings.issuer_id,
        _raw_private_key(settings.credentials_info["private_key"]),
    )
    decryptor.verify_signature(dict(data))
    return SignedMessage.model_validate(data.signedMessage)
