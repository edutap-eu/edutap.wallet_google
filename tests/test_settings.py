from edutap.wallet_google.session import GoogleWalletSettings
from pprint import pprint

import os
import pytest


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


@pytest.mark.skipif(
    os.environ.get("RUN_ON_CI", False), reason="should only be run locally"
)
def test_local_settings():
    settings = GoogleWalletSettings()
    print("Test Settings - Dump Settings Values:")
    # print(settings.model_dump())
    pprint(settings.model_dump(), indent=2, sort_dicts=True)

    assert settings.issuer_id is not None
    assert settings.credentials_file.exists()
