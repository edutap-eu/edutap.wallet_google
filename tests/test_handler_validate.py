"""Tests for handlers.validate module.

These tests verify the signature validation functions (async only).
"""

from edutap.wallet_google.models.handlers import CallbackData
from freezegun import freeze_time

import json
import pytest


callback_data_for_test_failure = {
    "signature": "foo",
    "intermediateSigningKey": {
        "signedKey": """{"keyValue": "baz", "keyExpiration": 0}""",
        "signatures": [
            "MEUCIQD3IATpRM45gpno9Remtx/FiDCOJUp45+C+Qzw6IrgphwIgJijXISc+Ft8Sj9eXNowzuYyXyWlgKAE+tVnN24Sek5M="
        ],
    },
    "protocolVersion": "ECv2SigningOnly",
    "signedMessage": json.dumps(
        {
            "classId": "1.1",
            "objectId": "2.1",
            "expTimeMillis": 0,
            "eventType": "save",
            "count": 0,
            "nonce": "fooo",
        }
    ),
}


callback_data = {
    "signature": "MEUCIQC+xKva1ydmNwJJiP2HJJWsteUe02ztTDKExzcWIpmlywIgJwD4HUYvZJg/cr1OL21vVKr0b2ZXt79NblCQ1V18zsc=",
    "intermediateSigningKey": {
        "signedKey": '{"keyValue":"MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEKb256ssDdmf7DokZ7jsMtAvjiTX2HF1ay8QR1sSA+gFpC/ChhRwVdMEVJTaoAP1MIH38QWtqShiQ63zROaKtgQ\\u003d\\u003d","keyExpiration":"1759996807000"}',
        "signatures": [
            "MEUCIDd7rXh7qgJZ7YSlQiXG2zOdZUT5XlMSUPu3RfyV3p2CAiEApxrIwTmRVig93FVJUC6bSWdQXMqata5sHenKsVYreUk="
        ],
    },
    "protocolVersion": "ECv2SigningOnly",
    "signedMessage": '{"classId":"3388000000022141777.lib.edutap.eu","objectId":"3388000000022141777.6b4cbd15-0de7-4fe8-95f6-995a51b4595e.object","eventType":"del","expTimeMillis":1759331348143,"count":1,"nonce":"1a9e3df0-ec10-4a17-8b39-89d2d7f48e3b"}',
}


@pytest.mark.asyncio
async def test_google_public_key_cached_empty(mock_settings):
    """Test that Google public keys can be fetched and cached (async)."""
    from edutap.wallet_google.handlers.validate import google_root_signing_public_keys

    keys = await google_root_signing_public_keys(mock_settings.google_environment)
    assert keys is not None

    from edutap.wallet_google.handlers.validate import (
        GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE,
    )

    # Cache structure is now (keys, expiration_timestamp)
    cached = GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE.get(
        mock_settings.google_environment, None
    )
    assert cached is not None
    keys_cached, expiration = cached
    assert keys_cached is not None
    assert expiration > 0

    # Second fetch should use cache
    keys2 = await google_root_signing_public_keys(mock_settings.google_environment)
    assert keys2 is not None


@pytest.mark.asyncio
@freeze_time("2025-10-01 12:00:00")
async def test_handler_validate_ok(mock_settings):
    """Test successful signature validation (async)."""
    from edutap.wallet_google.handlers.validate import verified_signed_message

    mock_settings.handler_callback_verify_signature = "1"

    data = CallbackData.model_validate(callback_data)
    message = await verified_signed_message(data)
    assert message.classId == "3388000000022141777.lib.edutap.eu"
    assert (
        message.objectId
        == "3388000000022141777.6b4cbd15-0de7-4fe8-95f6-995a51b4595e.object"
    )
    assert message.eventType == "del"


@pytest.mark.asyncio
async def test_handler_validate_invalid(mock_settings):
    """Test that invalid signature raises exception (async)."""
    from edutap.wallet_google.handlers.validate import verified_signed_message

    mock_settings.handler_callback_verify_signature = "1"

    data = CallbackData.model_validate(callback_data_for_test_failure)
    with pytest.raises(Exception):
        await verified_signed_message(data)


@pytest.mark.asyncio
@freeze_time("2025-10-01 12:00:00")
async def test_message_expiration_valid(mock_settings):
    """Test that a message with future expiration passes validation (async)."""
    from edutap.wallet_google.handlers.validate import verified_signed_message

    mock_settings.handler_callback_verify_signature = "1"

    # Use the valid callback data with expiration in the future
    data = CallbackData.model_validate(callback_data)
    message = await verified_signed_message(data)
    assert message.classId == "3388000000022141777.lib.edutap.eu"


@pytest.mark.asyncio
@freeze_time("2025-11-01 12:00:00")  # One month after the message expired
async def test_message_expiration_expired(mock_settings):
    """Test that an expired message raises ValueError with descriptive error (async)."""
    from edutap.wallet_google.handlers.validate import verified_signed_message

    mock_settings.handler_callback_verify_signature = "1"

    # callback_data has expTimeMillis: 1759331348143 (Oct 1, 2025 10:02:28 UTC)
    # We're frozen at Nov 1, 2025 12:00:00 UTC
    data = CallbackData.model_validate(callback_data)

    with pytest.raises(ValueError) as exc_info:
        await verified_signed_message(data)

    # Verify error message contains expiration details
    error_msg = str(exc_info.value)
    assert "Expired message" in error_msg
    assert "seconds ago" in error_msg
    assert "expTimeMillis" in error_msg


@pytest.mark.asyncio
@freeze_time("2025-10-01 10:01:00")  # Just before the message expires
async def test_message_expiration_just_before_expiry(mock_settings):
    """Test that a message just before expiration still passes (async)."""
    from edutap.wallet_google.handlers.validate import verified_signed_message

    mock_settings.handler_callback_verify_signature = "1"

    # callback_data expires at Oct 1, 2025 10:02:28 UTC
    # We're at Oct 1, 2025 10:01:00 UTC (88 seconds before expiry)
    data = CallbackData.model_validate(callback_data)
    message = await verified_signed_message(data)
    assert message.classId == "3388000000022141777.lib.edutap.eu"


@pytest.mark.asyncio
@freeze_time("2025-10-15 10:01:00")
async def test_message_expiration_expiry_check_ignored(mock_settings):
    """
    Test that the handler_callback_verify_expiry set to 0 disables
    check for key expiration (needed for testing) (async).
    """
    from edutap.wallet_google.handlers.validate import verified_signed_message

    mock_settings.handler_callback_verify_signature = "1"
    mock_settings.handler_callback_verify_expiry = "0"

    # callback_data expires at Oct 1, 2025 10:02:28 UTC
    # We're at Oct 15, 2025 10:01:00 UTC (data are expired for ~2 weeks)
    data = CallbackData.model_validate(callback_data)

    message = await verified_signed_message(data)
    assert message.classId == "3388000000022141777.lib.edutap.eu"


@pytest.mark.asyncio
async def test_cache_expiration_refresh(mock_settings):
    """Test that cache is refreshed when it expires (async)."""
    from edutap.wallet_google.handlers.validate import google_root_signing_public_keys
    from edutap.wallet_google.handlers.validate import (
        GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE,
    )

    import time

    # Clear cache
    GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE.clear()

    # First fetch - should cache (hits real API)
    keys1 = await google_root_signing_public_keys(mock_settings.google_environment)
    assert len(keys1.keys) >= 1

    # Verify cached
    cached = GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE.get(mock_settings.google_environment)
    assert cached is not None
    keys_cached, cache_exp = cached
    assert cache_exp > time.time()  # Should expire in future

    # Second fetch - should use cache
    keys2 = await google_root_signing_public_keys(mock_settings.google_environment)
    assert keys2 == keys1

    # Manually expire the cache
    GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE[mock_settings.google_environment] = (
        keys1,
        time.time() - 1,  # Expired 1 second ago
    )

    # Third fetch - should refresh due to expiration (hits real API again)
    keys3 = await google_root_signing_public_keys(mock_settings.google_environment)
    assert len(keys3.keys) >= 1

    # Verify cache was refreshed with new expiration
    cached_after = GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE.get(
        mock_settings.google_environment
    )
    _, cache_exp_after = cached_after
    assert cache_exp_after > time.time()  # New expiration in future


@pytest.mark.asyncio
async def test_signature_verification_disabled(mock_settings):
    """Test that signature verification can be disabled (async)."""
    from edutap.wallet_google.handlers.validate import verified_signed_message

    mock_settings.handler_callback_verify_signature = "0"

    # Even with invalid data, should pass when verification is disabled
    data = CallbackData.model_validate(callback_data_for_test_failure)
    message = await verified_signed_message(data)
    assert message.classId == "1.1"
    assert message.objectId == "2.1"


@pytest.mark.asyncio
@freeze_time("2025-10-01 12:00:00")
async def test_protocol_version_mismatch(mock_settings):
    """Test that mismatched protocol version raises error (async)."""
    from edutap.wallet_google.handlers.validate import verified_signed_message

    mock_settings.handler_callback_verify_signature = "1"

    # Create data with wrong protocol version
    invalid_callback = callback_data.copy()
    invalid_callback["protocolVersion"] = "ECv2"  # Wrong version

    data = CallbackData.model_validate(invalid_callback)
    with pytest.raises(ValueError) as exc_info:
        await verified_signed_message(data)

    assert "protocolVersion" in str(exc_info.value)
