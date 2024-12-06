from edutap.wallet_google.settings import GoogleWalletSettings
from edutap.wallet_google.settings import ROOT_DIR


def test_base_settings():
    settings = GoogleWalletSettings()

    assert (
        str(settings.base_url)
        == "https://walletobjects.googleapis.com/walletobjects/v1"
    )
    assert str(settings.save_url) == "https://pay.google.com/gp/v/save"
    assert [str(s) for s in settings.scopes] == [
        "https://www.googleapis.com/auth/wallet_object.issuer"
    ]


def test_local_settings(monkeypatch):
    monkeypatch.setenv(
        "EDUTAP_WALLET_GOOGLE_ISSUER_ID",
        "1234567890123456789",
    )
    monkeypatch.setenv(
        "EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE",
        str(ROOT_DIR / "tests" / "data" / "credentials_fake.json"),
    )

    settings = GoogleWalletSettings()

    assert settings.issuer_id == "1234567890123456789"
    assert settings.credentials_file.exists()
