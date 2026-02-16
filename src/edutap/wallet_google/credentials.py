from .settings import Settings

import functools
import json


class CredentialsManager:
    """Manages credential loading and caching.

    This class provides credential loading functionality without depending on
    google-auth or authlib. It simply reads and caches credentials from a file.
    """

    @property
    def settings(self) -> Settings:
        settings = getattr(self, "_settings", None)
        if settings is None:
            self._settings = Settings()
        return self._settings

    @functools.cache
    def credentials_from_file(self) -> dict:
        """Load credentials from file defined in settings.

        :return: Credentials as dict.
        :raises ValueError: When credentials file does not exist.
        """
        credentials_file = self.settings.credentials_file
        if not credentials_file.is_file():
            raise ValueError(f"Credentials file {credentials_file} not exists")
        with credentials_file.open() as fd:
            return json.loads(fd.read())


# Singleton instance
credentials_manager = CredentialsManager()
