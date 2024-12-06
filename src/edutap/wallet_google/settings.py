from .models.callback import RootSigningPublicKeys
from pathlib import Path
from pydantic import EmailStr
from pydantic import Field
from pydantic import HttpUrl
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from typing import Literal

import requests


ENV_PREFIX = "EDUTAP_WALLET_GOOGLE_"
ROOT_DIR = Path(__file__).parent.parent.parent.parent.resolve()
BASE_URL = "https://walletobjects.googleapis.com/walletobjects/v1"
SAVE_URL = "https://pay.google.com/gp/v/save"
SCOPE = "https://www.googleapis.com/auth/wallet_object.issuer"
GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_URL = {
    # see https://developers.google.com/pay/api/android/guides/resources/payment-data-cryptography#root-signing-keys
    "testing": {
        "url": "https://payments.developers.google.com/paymentmethodtoken/test/keys.json",
        "value": None,
    },
    "production": {
        "url": "https://payments.developers.google.com/paymentmethodtoken/keys.json",
        "value": None,
    },
}


class GoogleWalletSettings(BaseSettings):
    """Settings for Google Wallet Preferences.

    For more on how these settings work follow https://docs.pydantic.dev/latest/concepts/pydantic_settings/

    Any default can be overridden by setting the corresponding environment variable prefixed with `EDUTAP_WALLET_GOOGLE_`.
    If a `.env` file is present in the root directory of the project, the environment variables will be loaded from there.
    """

    model_config = SettingsConfigDict(
        env_prefix=ENV_PREFIX,
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    record_api_calls_dir: Path | None = None  # ROOT_DIR / "tests" / "data"
    base_url: HttpUrl = HttpUrl(BASE_URL)
    save_url: HttpUrl = HttpUrl(SAVE_URL)
    scopes: list[str] = [SCOPE]

    credentials_file: Path = ROOT_DIR / "credentials.json"
    issuer_account_email: EmailStr | None = None
    issuer_id: str | None = Field(min_length=19, max_length=20, default=None)

    callback_url: HttpUrl | None = None
    callback_update_url: HttpUrl | None = None

    environment: Literal["production", "testing"] = "testing"

    google_root_signing_public_keys: RootSigningPublicKeys | None = None

    def __init__(self):
        super().__init__()
        if GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_URL[self.environment]["value"] is None:
            resp = requests.get(
                GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_URL[self.environment]["url"]
            )
            resp.raise_for_status()
            self.google_root_signing_public_keys = (
                RootSigningPublicKeys.model_validate_json(resp.text)
            )
        else:
            self.google_root_signing_public_keys = GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_URL[
                self.environment
            ]["value"]
