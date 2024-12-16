from edutap.wallet_google._vendor.google_pay_token_decryption import GooglePayError
from edutap.wallet_google.models.callback import CallbackData

import json
import pytest


callbackdata_for_test_failure = {
    "signature": "foo",
    "intermediateSigningKey": {
        "signedKey": {"keyValue": "baz", "keyExpiration": 0},
        "signatures": ["bar"],
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


def test_handler_validate_invalid(mock_settings):
    from edutap.wallet_google.handlers.validate import verified_signed_message

    mock_settings.callback_verify_signature = True

    data = CallbackData.model_validate(callbackdata_for_test_failure)
    with pytest.raises(GooglePayError):
        verified_signed_message(data)
