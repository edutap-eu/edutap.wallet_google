from .credentials import credentials_manager
from .registry import lookup_metadata_by_name
from .settings import Settings
from authlib.integrations.httpx_client import AssertionClient
from authlib.integrations.httpx_client import AsyncAssertionClient

import httpx
import json


class HTTPRecorder(httpx.Client):
    """Record the HTTP requests and responses to a file."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = Settings()

    def request(self, method, url, *args, **kwargs):
        # Record request
        body_data = kwargs.get("data") or kwargs.get("content") or kwargs.get("json")
        if body_data:
            if isinstance(body_data, bytes):
                body_json = json.loads(body_data.decode("utf-8"))
            elif isinstance(body_data, str):
                body_json = json.loads(body_data)
            else:
                # Already a dict or other object (including json= parameter)
                body_json = body_data
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
    """Manages both sync and async sessions to the Google Wallet API.

    Provides session managers for both synchronous and asynchronous operations:
    - session() returns AssertionClient (sync)
    - async_session() returns AsyncAssertionClient (async)

    Both should be used as context managers for proper resource cleanup.
    All API functions in api.py use context managers automatically.
    """

    def __init__(self):
        self.settings = Settings()

    def _get_credentials(self, credentials: dict | None) -> dict:
        """Get credentials from parameter or load from file.

        :param credentials: Optional credentials dict.
        :return:            Credentials dict.
        """
        if not credentials:
            credentials = credentials_manager.credentials_from_file()
        return credentials

    def _build_session_config(self, credentials: dict) -> dict:
        """Build common session configuration for both sync and async clients.

        :param credentials: Service account credentials dict.
        :return:            Configuration dict for AssertionClient/AsyncAssertionClient.
        """
        token_endpoint = "https://oauth2.googleapis.com/token"
        return {
            "token_endpoint": token_endpoint,
            "issuer": credentials["client_email"],
            "subject": credentials["client_email"],
            "audience": token_endpoint,
            "claims": {
                "scope": " ".join(self.settings.credentials_scopes),
            },
            "key": credentials["private_key"],
            "key_id": credentials["private_key_id"],
            "header": {"alg": "RS256", "typ": "JWT"},
        }

    def session(self, credentials: dict | None = None) -> AssertionClient:
        """Create and return a sync authorized session.

        The returned AssertionClient should be used as a context manager:
        with session_manager.session() as session:
            response = session.get(url)

        All API functions in api.py use context managers automatically for proper cleanup.

        :param credentials: Session credentials as dict. If not given, credentials
                            are read from file defined in settings.
        :return:            The assertion client (httpx-based).
        """
        credentials = self._get_credentials(credentials)
        config = self._build_session_config(credentials)

        # Use HTTPRecorder if recording is enabled
        if self.settings.record_api_calls_dir is not None:
            config["client_cls"] = HTTPRecorder

        return AssertionClient(**config)

    def async_session(self, credentials: dict | None = None) -> AsyncAssertionClient:
        """Create and return an async authorized session.

        The returned AsyncAssertionClient should be used as an async context manager:
        async with session_manager.async_session() as session:
            response = await session.get(url)

        All async API functions in api.py use context managers automatically for proper cleanup.

        :param credentials: Session credentials as dict. If not given, credentials
                            are read from file defined in settings.
        :return:            The async assertion client.
        """
        credentials = self._get_credentials(credentials)
        config = self._build_session_config(credentials)
        # Note: AsyncAssertionClient doesn't support client_cls parameter for custom clients
        return AsyncAssertionClient(**config)

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


# Singleton instances for both sync and async operations
session_manager = SessionManager()
# Backward compatibility: both point to same instance
session_manager_async = session_manager
