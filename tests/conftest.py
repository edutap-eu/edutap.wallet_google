import copy
import pytest

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
    from edutap.wallet_google.session import SessionManager
    from edutap.wallet_google.session import _THREADLOCAL

    _THREADLOCAL.session = None

    def mock_session():
        return requests_mock

    monkeypatch.setattr(SessionManager, "session", property(mock_session()))

    yield requests_mock

    _THREADLOCAL.session = None
