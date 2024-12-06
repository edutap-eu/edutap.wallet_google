from pathlib import Path
from pydantic import EmailStr
from pydantic import Field
from pydantic import HttpUrl
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


ENV_PREFIX = "EDUTAP_WALLET_GOOGLE_"
ROOT_DIR = Path(__file__).parent.parent.parent.parent.resolve()
BASE_URL = "https://walletobjects.googleapis.com/walletobjects/v1"
SAVE_URL = "https://pay.google.com/gp/v/save"
SCOPE = "https://www.googleapis.com/auth/wallet_object.issuer"


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
