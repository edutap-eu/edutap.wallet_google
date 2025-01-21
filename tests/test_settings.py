from edutap.wallet_google.settings import ROOT_DIR
from edutap.wallet_google.settings import Settings

import pathlib
import pytest


def test_base_settings():
    settings = Settings()

    assert (
        str(settings.api_url) == "https://walletobjects.googleapis.com/walletobjects/v1"
    )
    assert str(settings.save_url) == "https://pay.google.com/gp/v/save"
    assert [str(s) for s in settings.credentials_scopes] == [
        "https://www.googleapis.com/auth/wallet_object.issuer"
    ]


def test_local_settings(monkeypatch):
    monkeypatch.setenv(
        "EDUTAP_WALLET_GOOGLE_TEST_ISSUER_ID",
        "1234567890123456789",
    )
    monkeypatch.setenv(
        "EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE",
        str(ROOT_DIR / "tests" / "data" / "credentials_fake.json"),
    )

    settings = Settings()

    assert settings.test_issuer_id == "1234567890123456789"
    assert settings.credentials_file.exists()


def test_settings_cached(mock_settings):
    mock_settings.cached_credentials_info = "test"
    assert mock_settings.credentials_info == "test"


def test_settings_no_credentials_file(mock_settings):
    mock_settings.credentials_file = pathlib.Path("nonexistent.json")
    with pytest.raises(FileNotFoundError):
        mock_settings.credentials_info


def test_settings_wrong_credentials_file(mock_settings):
    mock_settings.credentials_file = (
        ROOT_DIR / "tests" / "data" / "credentials_fake_wrong.json"
    )
    with pytest.raises(ValueError):
        mock_settings.credentials_info
