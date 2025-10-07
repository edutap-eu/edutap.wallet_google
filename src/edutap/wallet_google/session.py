from .credentials import credentials_manager
from .registry import lookup_metadata_by_name
from .settings import Settings
from authlib.integrations.httpx_client import AssertionClient

import httpx
import json
import threading


_THREADLOCAL = threading.local()


class HTTPRecorder(httpx.Client):
    """Record the HTTP requests and responses to a file."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._settings = Settings()

    @property
    def settings(self) -> Settings:
        return self._settings

    def request(self, method, url, *args, **kwargs):
        # Record request
        body_data = kwargs.get("data") or kwargs.get("content")
        if body_data:
            if isinstance(body_data, bytes):
                body_json = json.loads(body_data.decode("utf-8"))
            else:
                body_json = json.loads(body_data)
        else:
            body_json = None

        req_record = {
            "method": method,
            "url": str(url),
            "headers": dict(kwargs.get("headers", {})),
            "body": body_json,
        }
        target_directory = self.settings.record_api_calls_dir
        if not target_directory.exists():
            target_directory.mkdir(parents=True)
        filename = (
            f"{target_directory}/{method}-{str(url).replace('/', '_')}.REQUEST.json"
        )
        with open(filename, "w") as fp:
            json.dump(req_record, fp, indent=4)

        # Make the actual request
        response = super().request(method, url, *args, **kwargs)

        # Record response
        resp_record = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": (
                response.json()
                if response.headers.get("content-type", "").startswith(
                    "application/json"
                )
                else response.text
            ),
        }
        with open(filename.replace("REQUEST", "RESPONSE"), "w") as fp:
            json.dump(resp_record, fp, indent=4)
        return response


class SessionManager:
    """Manages the session to the Google Wallet API and provides helper methods.

    Sessions here are thread safe and use httpx with authlib for OAuth2.
    """

    @property
    def settings(self) -> Settings:
        settings = getattr(self, "_settings", None)
        if settings is None:
            self._settings = Settings()
        return self._settings

    def _make_session(self, credentials: dict) -> AssertionClient:
        """Create an OAuth2 service account client using Authlib and httpx.

        :param credentials: Service account credentials as dict.
        :return:            The assertion client.
        """
        token_endpoint = "https://oauth2.googleapis.com/token"

        # Use HTTPRecorder if recording is enabled
        if self.settings.record_api_calls_dir is not None:
            client_class = HTTPRecorder
        else:
            client_class = None

        client = AssertionClient(
            token_endpoint=token_endpoint,
            issuer=credentials["client_email"],
            subject=credentials["client_email"],
            audience=token_endpoint,
            claims={
                "scope": " ".join(self.settings.credentials_scopes),
            },
            key=credentials["private_key"],
            key_id=credentials["private_key_id"],
            header={"alg": "RS256", "typ": "JWT"},
            client_cls=client_class,
        )

        return client

    def session(self, credentials: dict | None = None) -> AssertionClient:
        """
        Create and return an authorized session.

        :param credentials: Session credentials as dict. If not given, credentials
                            are read from file defined in settings.
        :return:            The assertion client (httpx-based).
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
