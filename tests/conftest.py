from pathlib import Path

import copy
import json
import pytest

DATA_PATH = Path(__file__).parent / "data"



@pytest.fixture
def clean_registry():
    """Fixture to provide a clean the google_wallet model registry."""
    from edutap.wallet_google.registry import _MODEL_REGISTRY

    OLD_MODEL_REGISTRY = copy.deepcopy(_MODEL_REGISTRY)
    _MODEL_REGISTRY.clear()
    yield _MODEL_REGISTRY
    _MODEL_REGISTRY.clear()
    _MODEL_REGISTRY.update(OLD_MODEL_REGISTRY)


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
    def _load_mock_request_response(name: str, url: str, method: str, code=200):
        data = {}
        for postfix in {"REQUEST", "RESPONSE"}:
            with open(DATA_PATH / f"{name}.REQUEST.json", "r") as f:
                data[postfix.lower()] = json.load(f)
        mock_session.register_uri(method, url, json=data["response"]["body"], status_code=code)
        return data["request"]

    yield _load_mock_request_response
