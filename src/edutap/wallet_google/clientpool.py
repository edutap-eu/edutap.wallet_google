import atexit
import threading

from authlib.integrations.httpx_client import AssertionClient, AsyncAssertionClient

from .credentials import credentials_manager
from .registry import lookup_metadata_by_name
from .settings import Settings


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
        # Register cleanup handler to close sync clients on process exit
        atexit.register(self.close_all_clients)

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
        if client := self._sync_clients.get(key, None):
            return client

        # Thread-safe client creation (only create once per credentials)
        with self._lock:
            config = self._build_client_config(credentials)
            client = AssertionClient(**config)
            self._sync_clients[key] = client
        return client

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
        if client := self._async_clients.get(key, None):
            return client

        # Thread-safe client creation (only create once per credentials)
        with self._lock:
            config = self._build_client_config(credentials)
            # Note: AsyncAssertionClient doesn't support client_cls parameter for custom clients
            client = AsyncAssertionClient(**config)
            self._async_clients[key] = client
        return client

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
