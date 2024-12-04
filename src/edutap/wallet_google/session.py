from .registry import lookup_metadata
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.service_account import Credentials
from pathlib import Path
from pydantic import EmailStr
from pydantic import Field
from pydantic import HttpUrl
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from requests.adapters import HTTPAdapter

import json
import threading


_THREADLOCAL = threading.local()

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


class HTTPRecorder(HTTPAdapter):
    """Record the HTTP requests and responses to a file."""

    def __init__(self, settings: GoogleWalletSettings):
        super().__init__()
        self.settings = settings

    def send(self, request, *args, **kwargs):
        req_record = {
            "method": request.method,
            "url": request.url,
            "headers": dict(request.headers),
            "body": json.loads(request.body.decode("utf-8")),
        }
        target_directory = self.settings.record_api_calls_dir
        if target_directory.is_dir() and not target_directory.exists():
            target_directory
        filename = f"{target_directory}/{request.method}-{request.url.replace('/', '_')}.REQUEST.json"
        with open(filename, "w") as fp:
            json.dump(req_record, fp, indent=4)
        response = super().send(request, *args, **kwargs)
        resp_record = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.json(),
        }
        with open(filename.replace("REQUEST", "RESPONSE"), "w") as fp:
            json.dump(resp_record, fp, indent=4)
        return response


class SessionManager:
    """Manages the session to the Google Wallet API and provides helper methods.

    Sessions here are thread safe.
    """

    def __init__(self):
        self.settings = GoogleWalletSettings()

    @property
    def credentials_info(self) -> dict[str, str]:
        if not self.settings.credentials_file.exists:
            raise ValueError(
                f"EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE={self.settings.credentials_file} does not exist."
            )
        with open(self.settings.credentials_file) as fp:
            self._credentials_info = json.load(fp)
        if not isinstance(self._credentials_info, dict):
            raise ValueError(
                f"EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE={self.settings.credentials_file} content is not a dict"
            )
        return self._credentials_info

    def _make_session(self) -> AuthorizedSession:
        if not self.settings.credentials_file.exists:
            raise ValueError(
                f"EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE={self.settings.credentials_file} does not exist."
            )
        credentials = Credentials.from_service_account_file(
            str(self.settings.credentials_file), scopes=self.settings.scopes
        )
        session = AuthorizedSession(credentials)
        if (
            self.settings.record_api_calls_dir is not None
            and self.settings.credentials_file.exists()
        ):
            session.mount("https://", HTTPRecorder(settings=self.settings))
        return session

    @property
    def session(self) -> AuthorizedSession:
        if getattr(_THREADLOCAL, "session", None) is None:
            _THREADLOCAL.session = self._make_session()
        return _THREADLOCAL.session  # type: ignore

    def url(self, name: str, additional_path: str = "") -> str:
        """
        Create the URL for the CRUD operations.

        :param name:            Registered name of the model.
        :param additional_path: Append this to the path.
                                Must start with a forward slash.

        :return: the url of the google RESTful API endpoint to handle this model
        """
        model_metadata = lookup_metadata(name)
        return f"{self.settings.base_url}/{model_metadata['url_part']}{additional_path}"


session_manager = SessionManager()
