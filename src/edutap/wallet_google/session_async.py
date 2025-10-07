from .credentials import credentials_manager
from .registry import lookup_metadata_by_name
from .settings import Settings
from authlib.integrations.httpx_client import AsyncAssertionClient


class AsyncSessionManager:
    """Manages async sessions to the Google Wallet API and provides helper methods.

    Sessions are async-safe and use httpx.AsyncClient with OAuth2 service account authentication.

    The session() method returns an AsyncAssertionClient that should be used as an async context manager
    to ensure proper resource cleanup. All API functions in api_async.py use context managers automatically.
    """

    def __init__(self):
        self.settings = Settings()

    def _make_session(self, credentials: dict) -> AsyncAssertionClient:
        """Create an async OAuth2 service account client using Authlib.

        :param credentials: Service account credentials as dict.
        :return:            The async assertion client.
        """
        token_endpoint = "https://oauth2.googleapis.com/token"

        client = AsyncAssertionClient(
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
        )

        return client

    def session(self, credentials: dict | None = None) -> AsyncAssertionClient:
        """
        Create and return an async authorized session.

        The returned AsyncAssertionClient should be used as an async context manager:
        async with session_manager.session() as session:
            response = await session.get(url)

        All API functions in api_async.py use context managers automatically for proper cleanup.

        :param credentials: Session credentials as dict. If not given, credentials
                            are read from file defined in settings.
        :return:            The async assertion client.
        """
        if not credentials:
            credentials = credentials_manager.credentials_from_file()

        return self._make_session(credentials)

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


session_manager_async = AsyncSessionManager()
