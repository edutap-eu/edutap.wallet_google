from .models.callback import RootSigningPublicKeys
from pathlib import Path
from pydantic import EmailStr
from pydantic import Field
from pydantic import HttpUrl
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from typing import Literal

import json
import requests


ENV_PREFIX = "EDUTAP_WALLET_GOOGLE_"
ROOT_DIR = Path(__file__).parent.parent.parent.parent.resolve()
API_URL = "https://walletobjects.googleapis.com/walletobjects/v1"
SAVE_URL = "https://pay.google.com/gp/v/save"
SCOPE = "https://www.googleapis.com/auth/wallet_object.issuer"
GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_URL = {
    # see https://developers.google.com/pay/api/android/guides/resources/payment-data-cryptography#root-signing-keys
    "testing": "https://payments.developers.google.com/paymentmethodtoken/test/keys.json",
    "production": "https://payments.developers.google.com/paymentmethodtoken/keys.json",
}
GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE: dict[str, RootSigningPublicKeys] = {}


class Settings(BaseSettings):
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

    record_api_calls_dir: Path | None = None
    api_url: HttpUrl = HttpUrl(API_URL)
    save_url: HttpUrl = HttpUrl(SAVE_URL)
    callback_url: HttpUrl | None = None
    callback_prefix: str = "/googlewallet"

    scopes: list[str] = [SCOPE]

    credentials_file: Path = ROOT_DIR / "tests" / "data" / "credentials_fake.json"
    issuer_account_email: EmailStr | None = None
    issuer_id: str = Field(default="")

    environment: Literal["production", "testing"] = "testing"

    cached_credentials_info: dict[str, str] = {}

    @property
    def google_root_signing_public_keys(self) -> RootSigningPublicKeys:
        """
        Fetch Googles root signing keys once for the configured environment and return them or the cached value.
        """
        if (
            GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE.get(self.environment, None)
            is not None
        ):
            return GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_VALUE[self.environment]
        # fetch once
        resp = requests.get(GOOGLE_ROOT_SIGNING_PUBLIC_KEYS_URL[self.environment])
        resp.raise_for_status()
        return RootSigningPublicKeys.model_validate_json(resp.text)

    @property
    def credentials_info(self) -> dict[str, str]:
        if credentials_info := self.cached_credentials_info:
            return credentials_info
        if not self.credentials_file.exists():
            raise ValueError(
                f"EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE={self.credentials_file} does not exist."
            )
        with open(self.credentials_file) as fp:
            self.cached_credentials_info = json.load(fp)
        if not isinstance(self.cached_credentials_info, dict):
            raise ValueError(
                f"EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE={self.credentials_file} content is not a dict"
            )
        return self.cached_credentials_info
