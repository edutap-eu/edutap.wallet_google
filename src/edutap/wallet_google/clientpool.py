from .credentials import credentials_manager
from .registry import lookup_metadata_by_name
from .settings import Settings
from authlib.integrations.httpx_client import AssertionClient
from authlib.integrations.httpx_client import AsyncAssertionClient

import atexit
import httpx
import json
import threading


class HTTPRecorder(httpx.Client):
    """Record the HTTP requests and responses to a file."""

    def __init__(self, *args, record_dir=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.record_dir = record_dir

    def request(self, method, url, *args, **kwargs):
        # If no recording directory configured, just pass through
        if self.record_dir is None:
            return super().request(method, url, *args, **kwargs)

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
        target_directory = self.record_dir
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


class ClientPoolManager:
    """Manages HTTP client pool for the Google Wallet API.

    Maintains persistent, pooled clients for efficient connection reuse:
    - client() returns cached AssertionClient (sync) - one per credentials set
    - async_client() returns cached AsyncAssertionClient (async) - one per credentials set

    Clients are reused across multiple API calls for optimal connection pooling.
    All API functions in api.py reuse these persistent clients automatically.

    Call close_all_clients() or aclose_all_clients() at application shutdown.
    """

    def __init__(self):
        self.settings = Settings()
        self._sync_clients = {}  # {credentials_key: AssertionClient}
        self._async_clients = {}  # {credentials_key: AsyncAssertionClient}
        self._lock = threading.Lock()  # Thread-safe client creation

    def _get_credentials(self, credentials: dict | None) -> dict:
        """Get credentials from parameter or load from file.

        :param credentials: Optional credentials dict.
        :return:            Credentials dict.
        """
        if not credentials:
            credentials = credentials_manager.credentials_from_file()
        return credentials

    def _get_credentials_key(self, credentials: dict) -> str:
        """Create a hashable key from credentials for client caching.

        Uses client_email and private_key_id as the identifier to ensure
        that key rotation results in a new client being cached.

        :param credentials: Credentials dict.
        :return:            String key for caching.
        """
        return f"{credentials['client_email']}:{credentials['private_key_id']}"

    def _build_client_config(self, credentials: dict) -> dict:
        """Build common client configuration for both sync and async clients.

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

    def client(self, credentials: dict | None = None) -> AssertionClient:
        """Get or create a persistent sync HTTP client from the pool.

        Returns a cached AssertionClient for the given credentials. The same client
        instance is reused across multiple API calls for optimal connection pooling.

        The client is thread-safe and can be shared across threads.

        :param credentials: Client credentials as dict. If not given, credentials
                            are read from file defined in settings.
        :return:            The assertion client (httpx-based, persistent).
        """
        credentials = self._get_credentials(credentials)
        key = self._get_credentials_key(credentials)

        # Thread-safe client creation (only create once per credentials)
        with self._lock:
            if key not in self._sync_clients:
                config = self._build_client_config(credentials)

                # Use HTTPRecorder if recording is enabled
                if self.settings.record_api_calls_dir is not None:
                    config["client_cls"] = HTTPRecorder
                    config["record_dir"] = self.settings.record_api_calls_dir

                self._sync_clients[key] = AssertionClient(**config)

        return self._sync_clients[key]

    def async_client(self, credentials: dict | None = None) -> AsyncAssertionClient:
        """Get or create a persistent async HTTP client from the pool.

        Returns a cached AsyncAssertionClient for the given credentials. The same client
        instance is reused across multiple API calls for optimal connection pooling.

        The client is task-safe and can be shared across async tasks (within same event loop).

        :param credentials: Client credentials as dict. If not given, credentials
                            are read from file defined in settings.
        :return:            The async assertion client (persistent).
        """
        credentials = self._get_credentials(credentials)
        key = self._get_credentials_key(credentials)

        # Thread-safe client creation (only create once per credentials)
        with self._lock:
            if key not in self._async_clients:
                config = self._build_client_config(credentials)
                # Note: AsyncAssertionClient doesn't support client_cls parameter for custom clients
                self._async_clients[key] = AsyncAssertionClient(**config)

        return self._async_clients[key]

    def close_all_clients(self):
        """Close all cached sync clients.

        Call this method at application shutdown to properly close all
        persistent clients and release resources.

        This method is synchronous and closes only sync clients.
        For async clients, use aclose_all_clients().
        """
        with self._lock:
            for client in self._sync_clients.values():
                client.close()
            self._sync_clients.clear()

    async def aclose_all_clients(self):
        """Close all cached async clients.

        Call this method at application shutdown to properly close all
        persistent async clients and release resources.

        This method must be called from an async context.
        For sync clients, use close_all_clients().
        """
        # Don't need lock here since we're in async context
        for client in list(self._async_clients.values()):
            await client.aclose()
        self._async_clients.clear()

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


# Singleton instance for both sync and async operations
client_pool = ClientPoolManager()


# Register cleanup handler to close clients on process exit
def _cleanup_clients():
    """Close all clients on process exit."""
    client_pool.close_all_clients()


atexit.register(_cleanup_clients)
