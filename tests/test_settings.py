from edutap.wallet_google.session import GoogleWalletSettings
from pprint import pprint


def test_settings():
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
    assert settings.issuer_id is not None
    assert settings.credentials_file.exists()
