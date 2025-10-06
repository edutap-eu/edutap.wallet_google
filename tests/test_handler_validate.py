from edutap.wallet_google.handlers.validate import _verify_intermediate_signing_key
from edutap.wallet_google.handlers.validate import google_root_signing_public_keys
from edutap.wallet_google.models.handlers import CallbackData
from freezegun import freeze_time

import json
import pytest


def test_google_public_key_cached_empty(mock_settings):
    from edutap.wallet_google.handlers.validate import google_root_signing_public_keys

    assert google_root_signing_public_keys(mock_settings.google_environment) is not None

    from edutap.wallet_google.handlers.validate import (
        GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE,
    )

    # Cache structure is now (keys, expiration_timestamp)
    cached = GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE.get(
        mock_settings.google_environment, None
    )
    assert cached is not None
    keys, expiration = cached
    assert keys is not None
    assert expiration > 0
    assert google_root_signing_public_keys(mock_settings.google_environment) is not None


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
            "classId": "1",
            "objectId": "2",
            "expTimeMillis": 0,
            "eventType": "save",
            "count": 0,
            "nonce": "fooo",
        }
    ),
}


# @pytest.mark.skip(reason="Not implemented")
def test_handler_validate_invalid(mock_settings):
    from edutap.wallet_google.handlers.validate import verified_signed_message

    mock_settings.handler_callback_verify_signature = "1"

    data = CallbackData.model_validate(callback_data_for_test_failure)
    with pytest.raises(Exception):
        verified_signed_message(data)


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


@freeze_time("2025-10-01 12:00:00")
def test_handler_validate_ok(mock_settings):
    from edutap.wallet_google.handlers.validate import verified_signed_message

    mock_settings.handler_callback_verify_signature = "1"

    data = CallbackData.model_validate(callback_data)
    verified_signed_message(data)


def test_verify_intermediate_signing_key(mock_settings):
    data = CallbackData.model_validate(callback_data)
    root_keys = google_root_signing_public_keys(mock_settings.google_environment)
    _verify_intermediate_signing_key(root_keys, data.intermediateSigningKey)


def test_google_keys_include_protocol_version(mock_settings):
    """Test that Google's root signing keys include protocolVersion field.

    This is important because we filter keys by protocol version for security.
    If this test fails, it means Google changed their key format and we need
    to reconsider our protocol version filtering approach.
    """
    from edutap.wallet_google.handlers.validate import PROTOCOL_VERSION

    root_keys = google_root_signing_public_keys(mock_settings.google_environment)

    # Verify we got keys
    assert len(root_keys.keys) > 0, "No keys returned from Google"

    # Verify all keys have protocolVersion field
    for idx, key in enumerate(root_keys.keys):
        assert hasattr(
            key, "protocolVersion"
        ), f"Key {idx} missing protocolVersion field"
        assert key.protocolVersion is not None, f"Key {idx} has None protocolVersion"
        # Log what we found for debugging
        print(f"Key {idx}: protocolVersion={key.protocolVersion}")

    # Verify at least one key matches our expected protocol version
    matching_keys = [k for k in root_keys.keys if k.protocolVersion == PROTOCOL_VERSION]
    assert len(matching_keys) > 0, (
        f"No keys found with protocol version '{PROTOCOL_VERSION}'. "
        f"Found: {[k.protocolVersion for k in root_keys.keys]}"
    )


def test_cache_expiration_refresh(mock_settings):
    """Test that cache is refreshed when it expires."""
    from edutap.wallet_google.handlers.validate import (
        GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE,
    )

    import time

    # Clear cache
    GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE.clear()

    # First fetch - should cache (hits real API)
    keys1 = google_root_signing_public_keys(mock_settings.google_environment)
    assert len(keys1.keys) >= 1

    # Verify cached
    cached = GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE.get(mock_settings.google_environment)
    assert cached is not None
    keys_cached, cache_exp = cached
    assert cache_exp > time.time()  # Should expire in future

    # Second fetch - should use cache
    keys2 = google_root_signing_public_keys(mock_settings.google_environment)
    assert keys2 == keys1

    # Manually expire the cache
    GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE[mock_settings.google_environment] = (
        keys1,
        time.time() - 1,  # Expired 1 second ago
    )

    # Third fetch - should refresh due to expiration (hits real API again)
    keys3 = google_root_signing_public_keys(mock_settings.google_environment)
    assert len(keys3.keys) >= 1

    # Verify cache was refreshed with new expiration
    cached_after = GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE.get(
        mock_settings.google_environment
    )
    _, cache_exp_after = cached_after
    assert cache_exp_after > time.time()  # New expiration in future


def test_expired_keys_filtered_logic():
    """Test the logic for filtering expired keys."""
    from edutap.wallet_google.models.handlers import RootSigningPublicKey
    from edutap.wallet_google.models.handlers import RootSigningPublicKeys

    import time

    # Create test data with one expired and one valid key
    past_time = int((time.time() - 1000) * 1000)  # Expired
    future_time = int((time.time() + 7200) * 1000)  # 2 hours from now

    expired_key = RootSigningPublicKey(
        keyValue="ExpiredKeyValue==",
        protocolVersion="ECv2SigningOnly",
        keyExpiration=str(past_time),
    )
    valid_key = RootSigningPublicKey(
        keyValue="ValidKeyValue==",
        protocolVersion="ECv2SigningOnly",
        keyExpiration=str(future_time),
    )

    all_keys = RootSigningPublicKeys(keys=[expired_key, valid_key])

    # Filter logic (mimics what the code does)
    current_time_ms = time.time() * 1000
    valid_keys = [
        key
        for key in all_keys.keys
        if not hasattr(key, "keyExpiration")
        or not key.keyExpiration
        or float(key.keyExpiration) > current_time_ms
    ]

    # Should only get the valid one
    assert len(valid_keys) == 1
    assert "ValidKeyValue" in valid_keys[0].keyValue
    assert "ExpiredKeyValue" not in valid_keys[0].keyValue
