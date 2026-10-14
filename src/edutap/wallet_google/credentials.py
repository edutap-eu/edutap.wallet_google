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

    # functools.cache on a method normally risks a memory leak: it keeps
    # every `self` that ever called the method alive for the process
    # lifetime. Here there is exactly one `self` — the `credentials_manager`
    # singleton below, the only instance this class is ever constructed
    # into (see api.py and clientpool.py, which both import that singleton
    # rather than instantiating CredentialsManager themselves). That
    # instance is already kept alive for the whole process by the module
    # binding, so caching on it does not extend anything's lifetime further.
    @functools.cache  # noqa: B019
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
