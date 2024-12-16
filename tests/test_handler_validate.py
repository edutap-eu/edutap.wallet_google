from edutap.wallet_google._vendor.google_pay_token_decryption import GooglePayError
from edutap.wallet_google.models.callback import CallbackData

import pytest


callbackdata_for_test_failure = {
    "signature": "foo",
    "intermediateSigningKey": {
        "signedKey": {"keyValue": "baz", "keyExpiration": 0},
        "signatures": ["bar"],
    },
    "protocolVersion": "ECv2SigningOnly",
    "signedMessage": {
        "classId": "1",
        "objectId": "2",
        "expTimeMillis": 0,
        "eventType": "SAVE",
        "count": 0,
        "nonce": "3",
    },
}


def test_handler_validate_invalid():
    from edutap.wallet_google.handlers.validate import verified_signed_message

    data = CallbackData.model_validate(callbackdata_for_test_failure)
    with pytest.raises(GooglePayError):
        verified_signed_message(data)
