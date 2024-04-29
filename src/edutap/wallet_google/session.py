from .registry import lookup_metadata
from dotenv import load_dotenv
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
import os
import threading


load_dotenv()

_THREADLOCAL = threading.local()

ROOT_DIR = Path(__file__).parent.parent.parent.parent.resolve()
BASE_URL = "https://walletobjects.googleapis.com/walletobjects/v1"
SAVE_URL = "https://pay.google.com/gp/v/save"
SCOPES = ["https://www.googleapis.com/auth/wallet_object.issuer"]


class GoogleWalletSettings(BaseSettings):
    """Settings for Google Wallet Preferences."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="EDUTAP_WALLET_GOOGLE_",
        case_sensitive=False,
        # extra="ignore",
        extra="allow",
    )

    record_api_calls_dir: Path | None = None
    base_url: HttpUrl = HttpUrl("https://walletobjects.googleapis.com/walletobjects/v1")
    save_url: HttpUrl = HttpUrl("https://pay.google.com/gp/v/save")
    scopes: list[HttpUrl] = [
        HttpUrl("https://www.googleapis.com/auth/wallet_object.issuer")
    ]

    credentials_path: Path = ROOT_DIR

    credentials_file: str = "credentials.json"
    issuer_account_email: EmailStr | None = None
    issuer_id: str | None = Field(min_length=19, max_length=20)


class HTTPRecorder(HTTPAdapter):
    """Record the HTTP requests and responses to a file."""

    def send(self, request, *args, **kwargs):
        req_record = {
            "method": request.method,
            "url": request.url,
            "headers": dict(request.headers),
            "body": json.loads(request.body.decode("utf-8")),
        }
        target_directory = os.environ.get("EDUTAP_WALLET_GOOGLE_RECORD_API_CALLS_DIR")
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
    """Manages the session to the Google Wallet API and provides helper methods."""

    @property
    def base_url(self) -> str:
        return str(self.settings.base_url)
        # if getattr(self, "_base_url", None) is None:
        #     self._base_url = os.environ.get("EDUTAP_WALLET_GOOGLE_BASE_URL", BASE_URL)
        # return self._base_url

    @property
    def save_url(self) -> str:
        return str(self.settings.save_url)
        # if getattr(self, "_save_url", None) is None:
        #     self._save_url = os.environ.get("EDUTAP_WALLET_GOOGLE_SAVE_URL", SAVE_URL)
        # return self._save_url

    @property
    def credentials_file(self) -> Path | None:
        if getattr(self, "_credentials_file", None) is None:
            self._credentials_file = None
            path = self.settings.credentials_path / self.settings.credentials_file
            if path.exists():
                self._credentials_file = path
            # if os.environ.get("EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE"):
            #     path = Path(os.environ.get("CREDENTIAL_PATH", ".")) / Path(
            #         os.environ.get(
            #             "EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE",
            #             "credential_file.json",
            #         )
            #     )
            #     if path.exists():
            #         self._credentials_file = path
        return self._credentials_file

    @property
    def credentials_info(self) -> dict[str, str]:
        if not self.credentials_file:
            raise ValueError("EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE not set")
        with open(self.credentials_file) as fp:
            self._credentials_info = json.load(fp)
        if not isinstance(self._credentials_info, dict):
            raise ValueError(
                "EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE content is not a dict"
            )
        return self._credentials_info

    def _make_session(self) -> AuthorizedSession:
        self.settings = GoogleWalletSettings()
        if not self.credentials_file:
            raise ValueError("EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE not set")
        credentials = Credentials.from_service_account_file(
            self.credentials_file, scopes=SCOPES
        )
        session = AuthorizedSession(credentials)
        if os.environ.get("EDUTAP_WALLET_GOOGLE_RECORD_API_CALLS_DIR", None):
            session.mount("https://", HTTPRecorder())
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
        return f"{self.base_url}/{model_metadata['url_part']}{additional_path}"


session_manager = SessionManager()
