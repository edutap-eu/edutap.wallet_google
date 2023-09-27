from .registry import lookup_metadata
from dotenv import load_dotenv
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.service_account import Credentials
from requests.adapters import HTTPAdapter

import json
import os
import threading


load_dotenv()

_THREADLOCAL = threading.local()

BASE_URL = "https://walletobjects.googleapis.com/walletobjects/v1"
SAVE_URL = "https://pay.google.com/gp/v/save"
SCOPES = ["https://www.googleapis.com/auth/wallet_object.issuer"]


class HTTPRecorder(HTTPAdapter):
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
    @property
    def base_url(self) -> str:
        if getattr(self, "_base_url", None) is None:
            self._base_url = os.environ.get("EDUTAP_WALLET_GOOGLE_BASE_URL", BASE_URL)
        return self._base_url

    @property
    def save_url(self) -> str:
        if getattr(self, "_save_url", None) is None:
            self._save_url = os.environ.get("EDUTAP_WALLET_GOOGLE_SAVE_URL", SAVE_URL)
        return self._save_url

    @property
    def credentials_file(self) -> str | None:
        return os.environ.get("EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE")

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
