from .registry import lookup_metadata
from .settings import GoogleWalletSettings
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.service_account import Credentials
from requests.adapters import HTTPAdapter

import json
import threading


_THREADLOCAL = threading.local()


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
