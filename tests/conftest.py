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


@pytest.fixture
def mock_settings():
    from edutap.wallet_google.session import session_manager

    yield session_manager.settings
    del session_manager._settings


@pytest.fixture
def mock_fernet_encryption_key(mock_settings):
    mock_settings.fernet_encryption_key = "TDTPJVv24gha-jRX0apPgPpMDN2wX1kVSNNZdWXcz8E="


@pytest.fixture
def test_issuer_id():
    from edutap.wallet_google.session import session_manager

    yield session_manager.settings.test_issuer_id
