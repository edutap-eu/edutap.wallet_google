from edutap.wallet_google.session import GoogleWalletSettings
from edutap.wallet_google.session import ROOT_DIR
from pprint import pprint

import os


def test_base_settings():
    settings = GoogleWalletSettings()
    print("Test Settings - Dump Settings Values:")
    # print(settings.model_dump())
    pprint(settings.model_dump(), indent=2, sort_dicts=True)

    assert (
        str(settings.base_url)
        == "https://walletobjects.googleapis.com/walletobjects/v1"
    )
    assert str(settings.save_url) == "https://pay.google.com/gp/v/save"
    assert [str(s) for s in settings.scopes] == [
        "https://www.googleapis.com/auth/wallet_object.issuer"
    ]


def test_local_settings(monkeypatch):
    env = os.environ
    pprint(env)

    if env.get("CI"):
        monkeypatch.setenv(
            "EDUTAP_WALLET_GOOGLE_ISSUER_ID",
            "1234567890123456789",
        )
        monkeypatch.setenv(
            "EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE",
            ROOT_DIR / "tests" / "data" / "credentials_fake.json",
        )

    settings = GoogleWalletSettings()
    print("Test Settings - Dump Settings Values:")
    # print(settings.model_dump())
    pprint(settings.model_dump(), indent=2, sort_dicts=True)

    assert settings.issuer_id is not None
    if env.get("CI"):
        assert settings.issuer_id == "1234567890123456789"
    assert settings.credentials_file.exists()
