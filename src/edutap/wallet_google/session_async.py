from .registry import lookup_metadata_by_name
from .settings import Settings
from authlib.integrations.httpx_client import AsyncAssertionClient

import functools
import json


class AsyncSessionManager:
    """Manages async sessions to the Google Wallet API and provides helper methods.

    Sessions are async-safe and use httpx.AsyncClient with OAuth2 service account authentication.
    """

    @property
    def settings(self) -> Settings:
        settings = getattr(self, "_settings", None)
        if settings is None:
            self._settings = Settings()
        return self._settings

    @functools.cache
    def credentials_from_file(self) -> dict:
        credentials_file = self.settings.credentials_file
        if not credentials_file.is_file():
            raise ValueError(f"Credentials file {credentials_file} not exists")
        with credentials_file.open() as fd:
            return json.loads(fd.read())

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

        :param credentials: Session credentials as dict. If not given, credentials
                            are read from file defined in settings.
        :return:            The async assertion client.
        """
        if not credentials:
            credentials = self.credentials_from_file()

        # For async, we create a new client each time
        # Could cache by private_key_id if needed, but simpler to create fresh
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
