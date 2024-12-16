from pathlib import Path

import copy
import datetime
import json
import os
import pytest
import socket
import typing


DATA_PATH = Path(__file__).parent / "data"


@pytest.fixture
def clean_registry_by_name():
    """Fixture to provide a clean the google_wallet model registry."""
    from edutap.wallet_google.registry import _MODEL_REGISTRY_BY_NAME

    OLD_MODEL_REGISTRY_BY_NAME = copy.deepcopy(_MODEL_REGISTRY_BY_NAME)
    _MODEL_REGISTRY_BY_NAME.clear()
    yield _MODEL_REGISTRY_BY_NAME
    _MODEL_REGISTRY_BY_NAME.clear()
    _MODEL_REGISTRY_BY_NAME.update(OLD_MODEL_REGISTRY_BY_NAME)


@pytest.fixture
def clean_registry_by_model():
    """Fixture to provide a clean the google_wallet model registry."""
    from edutap.wallet_google.registry import _MODEL_REGISTRY_BY_MODEL

    OLD_MODEL_REGISTRY_BY_MODEL = copy.deepcopy(_MODEL_REGISTRY_BY_MODEL)
    _MODEL_REGISTRY_BY_MODEL.clear()
    yield _MODEL_REGISTRY_BY_MODEL
    _MODEL_REGISTRY_BY_MODEL.clear()
    _MODEL_REGISTRY_BY_MODEL.update(OLD_MODEL_REGISTRY_BY_MODEL)


@pytest.fixture
def mock_session(monkeypatch, requests_mock):
    """Fixture to provide a mock Google Wallet API session."""
    from edutap.wallet_google.session import _THREADLOCAL
    from edutap.wallet_google.session import SessionManager

    import requests

    _THREADLOCAL.session = None

    def mock_session(self):
        return requests.Session()

    monkeypatch.setattr(SessionManager, "session", property(mock_session))

    yield requests_mock

    _THREADLOCAL.session = None


@pytest.fixture
def mock_request_response(mock_session):
    """Fixture to load a mock request response from a json file.
    Prepares a mock response and status code for a given url and method.
    """

    def _load_mock_request_response(
        name: str, url: str, method: str, code=200
    ) -> dict[str, typing.Any]:
        data = {}
        for postfix in {"REQUEST", "RESPONSE"}:
            with open(DATA_PATH / f"{name}.REQUEST.json") as f:
                data[postfix.lower()] = json.load(f)
        mock_session.register_uri(
            method, url, json=data["response"]["body"], status_code=code
        )
        return data

    yield _load_mock_request_response


@pytest.fixture
def integration_test_id():
    prefix = os.environ.get(
        "EDUTAP_WALLET_GOOGLE_INTEGRATION_TEST_PREFIX", socket.gethostname()
    )
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%d_%H-%M-%S_%f"
    )
    yield f"{prefix}.{timestamp}"


# The code below was vendored from https://github.com/yoyowallet/google-pay-token-decryption
# Copyright is by its original authors at Yoyo Wallet <dev@yoyowallet.com>
# It is under the MIT License, as found here https://github.com/yoyowallet/google-pay-token-decryption/blob/5cd006da9687171c1e35b55507b671c6e4eb513d/pyproject.toml#L8

# google_wallet signature validation

_valid_signature = "MEQCIFBle+JsfsovRBeoFEYKWFAeBYFAhq0S+GtusiosjV4lAiAGcK9qfVpnqG6Hw8cbGBQ79beiAs6IIkBxBfeKDBR+kA=="


@pytest.fixture
def valid_signature():
    return valid_signature


@pytest.fixture
def encrypted_token():
    """
    Test tokens generated using the Tink test code:
    https://github.com/google/tink/blob/06aa21432e1985fea4ab26c26f6038895b22cce0/apps/paymentmethodtoken/src/test/java/com/google/crypto/tink/apps/paymentmethodtoken/PaymentMethodTokenRecipientTest.java#L1042-L1059
    """
    return {
        "signature": "MEYCIQCbtFh9UIf1Ty3NKZ2z0ZmL0SHwR30uiRGuRXk9ghpyrwIhANiZQ0Df6noxkQ6M652PcIPkk2m1PQhqiq4UhzvPQOYf",
        "intermediateSigningKey": {
            "signedKey": '{"keyValue":"MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE/1+3HBVSbdv+j7NaArdgMyoSAM43yRydzqdg1TxodSzA96Dj4Mc1EiKroxxunavVIvdxGnJeFViTzFvzFRxyCw==","keyExpiration":"1879409613939"}',
            "signatures": [_valid_signature],
        },
        "protocolVersion": "ECv2",
        "signedMessage": '{"encryptedMessage":"PeYi+ZnJs1Gei1dSOkItdfFG8Y81FvEI7dHE0sSrSU6OPnndftV/qDbbmXHmppoyP/2lhF+XsH93qzD3u46BRnxxPtetzGT0533rIraskTj8SZ6FVYY1Opfo7FECGk57FfF8aDaCSOoyTh1k0v6wdxVwEVvWqG1T/ij+u2KWOw5G1WSB/RVicni0Az13ModYb0KMdMws1USKlWxBfKU5PtxibVx4fZ95HYQ82qgHlV4ToKaUY7YWud1iEspmFsBMk0nh4t1hVxRzsxKUjMV1915qD5yq7k5n9YPao2mR9NJgLPDktsc4uf9bszzvnqhz3T1YID43QwX16yCyn/YxNVe3dJ1+S+BGyJ+vyKXp+Zh4SlIua2NFLwnR06Es3Kvl6LlOGasoPC/tMAWYLQlGsl+vHK3mrMZjC6KbOsXg+2mrlZwL+QOt3ih2jIPe","ephemeralPublicKey":"BD6pQKpy7yDebAX4qV0u/AfMYNQhOD+teyoa/5SsxwTGCoC1ZKHxNMb5BXvRmBcYGPNTx8+fAkEwzJ8GqbX/Q7E=","tag":"8gFteCvCuamX1RmL7ORdHqleyBf0N55OfAs80RYGgwc="}',
    }

@pytest.fixture
def google_pay_token_decryptor(root_signing_keys, recipient_id, private_key):
    return GooglePayTokenDecryptor(root_signing_keys, recipient_id, private_key)