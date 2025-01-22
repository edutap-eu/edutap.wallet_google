"""
Parts of this module are rewrites and borrows from from https://github.com/yoyowallet/google-pay-token-decryption
The above packages does not fulfill the needs we have here, but was a great starting point.
Copyright is by its original authors at Yoyo Wallet <dev@yoyowallet.com>
This file is under the MIT License, as found here https://github.com/yoyowallet/google-pay-token-decryption/blob/5cd006da9687171c1e35b55507b671c6e4eb513d/pyproject.toml#L8
"""

from ..models.handlers import CallbackData
from ..models.handlers import IntermediateSigningKey
from ..models.handlers import RootSigningPublicKeys
from ..models.handlers import SignedKey
from ..models.handlers import SignedMessage
from ..session import session_manager
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ec import ECDSA
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from cryptography.hazmat.primitives.serialization import load_der_private_key
from cryptography.hazmat.primitives.serialization import load_der_public_key
from typing import cast

import base64
import httpx
import time


PROTOCOL_VERSION = "ECv2SigningOnly"
ALGORITHM = ECDSA(hashes.SHA256())
GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_URL = {
    # see https://developers.google.com/pay/api/android/guides/resources/payment-data-cryptography#root-signing-keys
    "testing": "https://payments.developers.google.com/paymentmethodtoken/test/keys.json",
    "production": "https://payments.developers.google.com/paymentmethodtoken/keys.json",
}
GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE: dict[str, RootSigningPublicKeys] = {}


def google_root_signing_public_keys(google_environment: str) -> RootSigningPublicKeys:
    """
    Fetch Googles root signing keys once for the configured environment and return them or the cached value.
    """
    if GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE.get(google_environment, None) is not None:
        return GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE[google_environment]
    # fetch once
    resp = httpx.get(GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_URL[google_environment])
    resp.raise_for_status()
    GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE[google_environment] = (
        RootSigningPublicKeys.model_validate_json(resp.text)
    )
    return GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE[google_environment]


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


def _construct_signed_data(*args: str) -> bytes:
    """
    Construct the signed message from the list of its components by concatenating the
    byte length of each component in 4 bytes little-endian format plus the UTF-8 encoded
    component.

    See https://developers.google.com/pay/api/android/guides/resources/payment-data-cryptography#verify-signature
    or  https://developers.google.com/pay/api/android/guides/resources/payment-data-cryptography#how-to-construct-the-byte-string-for-intermediate-signing-key-signature
    for an example.
    """
    signed = b""
    for a in args:
        signed += len(a).to_bytes(4, byteorder="little")
        signed += bytes(a, "utf-8")
    return signed


def _load_public_key(key: str) -> EllipticCurvePublicKey:
    derdata = base64.b64decode(key)
    return cast(
        EllipticCurvePublicKey,
        load_der_public_key(derdata, default_backend()),
    )


def _load_private_key(key: str) -> EllipticCurvePrivateKey:
    derdata = base64.b64decode(key)
    return cast(
        EllipticCurvePrivateKey,
        load_der_private_key(derdata, None, default_backend()),
    )


def _verify_intermediate_signing_key(
    public_keys: RootSigningPublicKeys,
    intermediate_signing_key: IntermediateSigningKey,
) -> bool:
    """Check the intermediate signing keys signature against the Google root public keys.

    see https://developers.google.com/pay/api/android/guides/resources/payment-data-cryptography#verify-signature
    """
    signatures = [
        base64.decodebytes(bytes(sig, "utf-8"))
        for sig in intermediate_signing_key.signatures
    ]
    signed_data = _construct_signed_data(
        "Google",
        PROTOCOL_VERSION,
        intermediate_signing_key.signedKey,
    )
    for pkey in public_keys.keys:

        if pkey.protocolVersion != PROTOCOL_VERSION:
            continue

        public_key = _load_public_key(pkey.keyValue)
        for signature in signatures:
            try:
                public_key.verify(signature, signed_data, ALGORITHM)
            except (ValueError, InvalidSignature):
                # Invalid signature. Try the other signatures.
                ...
            else:
                # Valid signature was found
                return True
    return False


def verified_signed_message(data: CallbackData) -> SignedMessage:
    """
    Verifies the signature of the callback data.
    and returns the parsed SignedMessage
    """
    # parse message
    message = SignedMessage.model_validate_json(data.signedMessage)

    # get issuer_id
    if not message.classId or "." not in message.classId:
        raise ValueError("Missing classId")
    issuer_id = message.classId.split(".")[0]

    # shortcut if signature validation is disabled
    settings = session_manager.settings
    if settings.handler_callback_verify_signature == "0":
        return message

    if data.protocolVersion != PROTOCOL_VERSION:
        raise ValueError("Invalid protocolVersion")

    # check intermediate signing keys signature
    if not _verify_intermediate_signing_key(
        google_root_signing_public_keys(settings.google_environment),
        data.intermediateSigningKey,
    ):
        raise ValueError("Invalid intermediate signing key")

    # check intermediate signing keys expriration date
    intermediate_signing_key = SignedKey.model_validate_json(
        data.intermediateSigningKey.signedKey
    )
    if int(time.time() * 1000) > int(intermediate_signing_key.keyExpiration):
        raise ValueError("Expired intermediate signing key")

    # check signed message's signature
    intermediate_public_key = _load_public_key(intermediate_signing_key.keyValue)
    signature = base64.decodebytes(bytes(data.signature, "utf-8"))
    signed_data = _construct_signed_data(
        "GooglePayWallet",
        issuer_id,
        PROTOCOL_VERSION,
        data.signedMessage,
    )
    try:
        intermediate_public_key.verify(signature, signed_data, ALGORITHM)
    except (ValueError, InvalidSignature):
        raise ValueError("Invalid signature")

    return message
