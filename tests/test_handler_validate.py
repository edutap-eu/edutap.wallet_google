from edutap.wallet_google.handlers.validate import verify_signature
from edutap.wallet_google.models.callback import CallbackData


callbackdata_for_test_failure = {
    "signature": "foo",
    "intermediateSigningKey": {
        "signedKey": {"keyValue": "baz", "keyExpiration": 0},
        "signatures": ["bar"],
    },
    "protocolVersion": "",
    "signedMessage": {
        "classId": "1",
        "objectId": "2",
        "expTimeMillis": 0,
        "eventType": "SAVE",
    },
}


def test_handler_validate_valid():
    data = CallbackData.model_validate(callbackdata_for_test_failure)
    assert verify_signature(data) is False
