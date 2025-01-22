from pathlib import Path
from pydantic import Field
from pydantic import HttpUrl
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from typing import Literal

import json


ENV_PREFIX = "EDUTAP_WALLET_GOOGLE_"
ROOT_DIR = Path(__file__).parent.parent.parent.parent.resolve()
API_URL = "https://walletobjects.googleapis.com/walletobjects/v1"
SAVE_URL = "https://pay.google.com/gp/v/save"
SCOPES = ["https://www.googleapis.com/auth/wallet_object.issuer"]


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

    handler_prefix: str = "/wallet/google"
    handler_prefix_callback: str = ""
    handler_prefix_images: str = ""
    handler_callback_verify_signature: str = "1"
    handler_image_cache_control: str = "no-cache"
    handlers_callback_timeout: float = 5.0
    handlers_image_timeout: float = 5.0

    credentials_file: Path = ROOT_DIR / "tests" / "data" / "credentials_fake.json"
    credentials_scopes: list[str] = SCOPES
    test_issuer_id: str = Field(default="")

    fernet_encryption_key: str = ""

    google_environment: Literal["production", "testing"] = "testing"

    cached_credentials_info: dict[str, str] = {}

    @property
    def credentials_info(self) -> dict[str, str]:
        if credentials_info := self.cached_credentials_info:
            return credentials_info
        if not self.credentials_file.exists():
            raise FileNotFoundError(
                f"EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE={self.credentials_file} does not exist."
            )
        with open(self.credentials_file) as fp:
            self.cached_credentials_info = json.load(fp)
        if not isinstance(self.cached_credentials_info, dict):
            raise ValueError(
                f"EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE={self.credentials_file} content is not a dict"
            )
        return self.cached_credentials_info
