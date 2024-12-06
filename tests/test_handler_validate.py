from edutap.wallet_google.handlers.validate import verify_signature


def test_handler_validate_valid():
    assert verify_signature("data") is True
