"""
Parts of this module are rewrites and borrows from from https://github.com/yoyowallet/google-pay-token-decryption
The above packages does not fulfill the needs we have here, but was a great starting point.
Copyright is by its original authors at Yoyo Wallet <dev@yoyowallet.com>
This file is under the MIT License, as found here https://github.com/yoyowallet/google-pay-token-decryption/blob/5cd006da9687171c1e35b55507b671c6e4eb513d/pyproject.toml#L8

The google-pay-token-decryption uses ECv2 for verification and decryption of payment tokens.

We need something slightly different here, as we need to verify the signature of
Google Wallet callback data, which is similar, but not the same.

The main differences/steps are:

- We do not need to decrypt anything, only verify signatures
- we use protocolVersion "ECv2SigningOnly" instead of "ECv2"
- As in ECv2 we need to verify first the intermediate signing key against Google's root signing keys
- the root signing keys are fetched from a different URL: https://pay.google.com/gp/m/issuer/keys (as it seems not difference between testing and prod)
- the sender ID is "GooglePayPasses" instead of "GooglePay"
- Then we need to verify the signedMessage against the intermediate signing key
- The signedMessage is sent as a plain readable JSON string, not as a base64 encoded byte string

The main documentation for this is at https://developers.google.com/wallet/generic/use-cases/use-callbacks-for-saves-and-deletions
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
import logging
import time


logger = logging.getLogger(__name__)


PROTOCOL_VERSION = "ECv2SigningOnly"
ALGORITHM = ECDSA(hashes.SHA256())
GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_URL = {
    # see https://developers.google.com/wallet/generic/use-cases/use-callbacks-for-saves-and-deletions
    "testing": "https://pay.google.com/gp/m/issuer/keys",
    "production": "https://pay.google.com/gp/m/issuer/keys",
}
# Cache structure: {environment: (keys, cache_expiration_timestamp)}
GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE: dict[
    str, tuple[RootSigningPublicKeys, float]
] = {}
# Refresh cache 1 hour before first key expires (safety margin)
CACHE_REFRESH_MARGIN_MS = 3600000  # 1 hour in milliseconds


def _calculate_cache_expiration(keys: RootSigningPublicKeys) -> float:
    """Calculate when the cache should expire based on key expiration times.

    Returns the earliest key expiration timestamp (minus safety margin) as cache TTL.
    If a key has no expiration or all keys are expired, returns current time + 1 hour.
    """
    current_time_ms = time.time() * 1000
    valid_expirations = []

    for key in keys.keys:
        if hasattr(key, "keyExpiration") and key.keyExpiration:
            exp_ms = float(key.keyExpiration)
            # Only consider non-expired keys
            if exp_ms > current_time_ms:
                valid_expirations.append(exp_ms)

    if not valid_expirations:
        # No valid keys with expiration, cache for 1 hour
        logger.warning("No valid key expirations found, using 1-hour cache TTL")
        return (current_time_ms + CACHE_REFRESH_MARGIN_MS) / 1000

    # Use earliest expiration minus safety margin
    earliest_expiration = min(valid_expirations)
    cache_until = (earliest_expiration - CACHE_REFRESH_MARGIN_MS) / 1000
    logger.debug(
        f"Cache will expire at {cache_until} "
        f"(earliest key expires at {earliest_expiration / 1000})"
    )
    return cache_until


def google_root_signing_public_keys(google_environment: str) -> RootSigningPublicKeys:
    """
    Fetch Googles root signing keys for the configured environment.

    Keys are cached until the earliest key expires (with 1-hour safety margin).
    Expired keys are filtered out. Cache is automatically refreshed when expired.
    """
    current_time = time.time()
    cached = GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE.get(google_environment)

    # Check if we have valid cached keys
    if cached is not None:
        keys, cache_expiration = cached
        if current_time < cache_expiration:
            logger.debug(
                f"Using cached keys (expires in {cache_expiration - current_time:.0f}s)"
            )
            return keys
        logger.info("Cache expired, refreshing Google root signing keys")

    # Fetch from Google
    logger.info(
        f"Fetching Google root signing keys from {GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_URL[google_environment]}"
    )
    resp = httpx.get(GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_URL[google_environment])
    resp.raise_for_status()
    all_keys = RootSigningPublicKeys.model_validate_json(resp.text)

    # Filter out expired keys
    current_time_ms = time.time() * 1000
    valid_keys = [
        key
        for key in all_keys.keys
        if not hasattr(key, "keyExpiration")
        or not key.keyExpiration
        or float(key.keyExpiration) > current_time_ms
    ]

    if not valid_keys:
        logger.error(f"All {len(all_keys.keys)} keys from Google are expired!")
        raise ValueError("All Google root signing keys are expired")

    if len(valid_keys) < len(all_keys.keys):
        logger.warning(
            f"Filtered out {len(all_keys.keys) - len(valid_keys)} expired keys, "
            f"{len(valid_keys)} valid keys remaining"
        )

    # Create filtered keys object and calculate cache expiration
    filtered_keys = RootSigningPublicKeys(keys=valid_keys)
    cache_expiration = _calculate_cache_expiration(filtered_keys)

    # Cache the filtered keys with expiration
    GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE[google_environment] = (
        filtered_keys,
        cache_expiration,
    )
    logger.info(f"Cached {len(valid_keys)} valid keys until {cache_expiration}")

    return filtered_keys


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

    This function filters keys by protocolVersion before attempting verification for:
    - Security: Only uses keys explicitly designed for our protocol
    - Performance: Skips incompatible keys early in the verification process
    - Clarity: Provides clear logging when keys don't match expected protocol

    The protocol version filtering was re-enabled after testing confirmed that
    Google's callback signing keys consistently include the protocolVersion field
    with value "ECv2SigningOnly".

    see https://developers.google.com/pay/api/android/guides/resources/payment-data-cryptography#verify-signature
    """
    signatures = [
        base64.decodebytes(bytes(sig, "utf-8"))
        for sig in intermediate_signing_key.signatures
    ]
    signed_data = _construct_signed_data(
        session_manager.settings.sender_id,
        PROTOCOL_VERSION,
        intermediate_signing_key.signedKey,
    )
    for pkey in public_keys.keys:
        # Filter keys by protocol version for security and performance
        # Only attempt verification with keys matching our protocol version
        if pkey.protocolVersion != PROTOCOL_VERSION:
            logger.debug(
                f"Skipping key with protocol version '{pkey.protocolVersion}', "
                f"expected '{PROTOCOL_VERSION}'"
            )
            continue

        public_key = _load_public_key(pkey.keyValue)
        for signature in signatures:
            try:
                public_key.verify(signature, signed_data, ALGORITHM)
            except (ValueError, InvalidSignature) as e:
                # Invalid signature. Try the other signatures.
                logger.debug(f"Invalid signature attempt: {e}")
            else:
                # Valid signature was found
                return True

    # No valid signature found after checking all compatible keys
    logger.warning(
        f"No valid signature found. Checked {len(public_keys.keys)} key(s) "
        f"with protocol version '{PROTOCOL_VERSION}'"
    )
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
    # https://developers.google.com/wallet/generic/use-cases/use-callbacks-for-saves-and-deletions#verify-the-signature
    intermediate_public_key = _load_public_key(intermediate_signing_key.keyValue)
    signature = base64.decodebytes(bytes(data.signature, "utf-8"))
    signed_data = _construct_signed_data(
        settings.sender_id,
        issuer_id,
        PROTOCOL_VERSION,
        data.signedMessage,
    )
    logger.debug(f"Verifying signature: {data.signature}")
    logger.debug(f"Signed data length: {len(signed_data)} bytes")
    try:
        intermediate_public_key.verify(signature, signed_data, ALGORITHM)
    except (ValueError, InvalidSignature) as e:
        logger.debug(f"Signature verification failed: {e}")
        raise ValueError("Invalid signature")

    return message
