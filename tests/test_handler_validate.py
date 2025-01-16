from edutap.wallet_google.models.handlers import CallbackData

import json
import pytest


def test_google_public_key_cached_empty(mock_settings):
    from edutap.wallet_google.handlers.validate import google_root_signing_public_keys

    assert google_root_signing_public_keys(mock_settings.google_environment) is not None

    from edutap.wallet_google.handlers.validate import (
        GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE,
    )

    assert (
        GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE.get(
            mock_settings.google_environment, None
        )
        is not None
    )
    assert google_root_signing_public_keys(mock_settings.google_environment) is not None


callback_data_for_test_failure = {
    "signature": "foo",
    "intermediateSigningKey": {
        "signedKey": {"keyValue": "baz", "keyExpiration": 0},
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


@pytest.mark.skip(reason="Not implemented")
def test_handler_validate_invalid(mock_settings):
    from edutap.wallet_google.handlers.validate import verified_signed_message

    mock_settings.handler_callback_verify_signature = "1"

    data = CallbackData.model_validate(callback_data_for_test_failure)
    with pytest.raises(Exception):
        verified_signed_message(data)


callback_data = {
    "signature": "MEYCIQCyuBQo/Dao7yUBDUWK12ATFBDkUfJUnropjOaPbPiKEwIhAKXNiVrbNmydpEVIxXRz5z36f8HV2Meq/Td6tqt2+DYO",
    "intermediateSigningKey": {
        "signedKey": '{"keyValue":"MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE3JpSX3AU53vH+IpWBdsbqrL7Ey67QSERsDUztFt8q7t7PzVkh14SeYeokI1zSZiVAWnx4tXD1tCPbrvfFGB8OA\u003d\u003d","keyExpiration":"1735023986000"}',
        "signatures": [
            "MEUCIQD3IBTpRM45gpno9Remtx/FiDCOJUp45+C+Qzw6IrgphwIgJijXISc+Ft8Sj9eXNowzuYyXyWlgKAE+tVnN24Sek5M="
        ],
    },
    "protocolVersion": "ECv2SigningOnly",
    "signedMessage": '{"classId":"3388000000022141777.pass.gift.dev.edutap.eu","objectId":"3388000000022141777.9fd4e525-777c-4e0d-878a-b7993e211997","eventType":"save","expTimeMillis":1734366082269,"count":1,"nonce":"c1359b53-f2bb-4e8f-b392-9a560a21a9a0"}',
}


def test_handler_validate_ok(mock_settings):
    from edutap.wallet_google.handlers.validate import verified_signed_message

    mock_settings.handler_callback_verify_signature = "0"

    data = CallbackData.model_validate(callback_data)
    verified_signed_message(data)
