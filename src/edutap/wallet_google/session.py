from .credentials import credentials_manager
from .registry import lookup_metadata_by_name
from .settings import Settings
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.service_account import Credentials
from requests.adapters import HTTPAdapter

import json
import threading


_THREADLOCAL = threading.local()


class HTTPRecorder(HTTPAdapter):
    """Record the HTTP requests and responses to a file."""

    @property
    def settings(self) -> Settings:
        settings = getattr(self, "_settings", None)
        if settings is None:
            self._settings = Settings()
        return self._settings

    def send(self, request, *args, **kwargs):
        req_record = {
            "method": request.method,
            "url": request.url,
            "headers": dict(request.headers),
            "body": json.loads(request.body.decode("utf-8")),
        }
        target_directory = self.settings.record_api_calls_dir
        if target_directory.is_dir() and not target_directory.exists():
            target_directory.mkdir(parents=True)
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

    @property
    def settings(self) -> Settings:
        settings = getattr(self, "_settings", None)
        if settings is None:
            self._settings = Settings()
        return self._settings

    def _make_session(self, credentials: dict) -> AuthorizedSession:
        google_credentials = Credentials.from_service_account_info(
            credentials,
            scopes=self.settings.credentials_scopes,
        )
        session = AuthorizedSession(google_credentials)
        if self.settings.record_api_calls_dir is not None:
            session.mount("https://", HTTPRecorder())
        return session

    def session(self, credentials: dict | None = None) -> AuthorizedSession:
        """
        Create and return an authorized session.

        :param credentials: Session credentials as dict. If not given, credentials
                            are read from file defined in settings.
        :return:            The authorized session.
        """
        if not credentials:
            credentials = credentials_manager.credentials_from_file()
        cache_key = credentials["private_key_id"]
        if getattr(_THREADLOCAL, "sessions", None) is None:
            _THREADLOCAL.sessions = dict()
        if cache_key not in _THREADLOCAL.sessions:
            _THREADLOCAL.sessions[cache_key] = self._make_session(credentials)
        return _THREADLOCAL.sessions[cache_key]

    def url(self, name: str, additional_path: str = "") -> str:
        """
        Create the URL for the CRUD operations.

        :param name:            Registered name of the model.
        :param additional_path: Append this to the path.
                                Must start with a forward slash.

        :return:                The url of the google RESTful API endpoint to handle
                                this model
        """
        model_metadata = lookup_metadata_by_name(name)
        return f"{self.settings.api_url}/{model_metadata['url_part']}{additional_path}"


session_manager = SessionManager()
