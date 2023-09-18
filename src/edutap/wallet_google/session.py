from .registry import lookup_metadata
from dotenv import load_dotenv
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.service_account import Credentials

import json
import os
import threading


load_dotenv()

_THREADLOCAL = threading.local()

BASE_URL = "https://walletobjects.googleapis.com/walletobjects/v1"
SAVE_URL = "https://pay.google.com/gp/v/save"
SCOPES = ["https://www.googleapis.com/auth/wallet_object.issuer"]


class SessionManager:
    @property
    def base_url(self):
        if getattr(self, "_base_url", None) is None:
            self._base_url = os.environ.get("EDUTAP_WALLET_GOOGLE_BASE_URL", BASE_URL)
        return self._base_url

    @property
    def save_url(self):
        if getattr(self, "_save_url", None) is None:
            self._save_url = os.environ.get("EDUTAP_WALLET_GOOGLE_SAVE_URL", SAVE_URL)
        return self._save_url

    @property
    def credentials_file(self):
        return os.environ.get("EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE")

    @property
    def credentials_info(self):
        if getattr(self, "_credentials_info", None) is None:
            with open(self.credentials_file) as fp:
                self._credentials_info = json.load(fp)
        return self._credentials_info

    def _make_session(self):
        credentials = Credentials.from_service_account_file(
            self.credentials_file, scopes=SCOPES
        )
        return AuthorizedSession(credentials)

    @property
    def session(self):
        if getattr(_THREADLOCAL, "session", None) is None:
            _THREADLOCAL.session = self._make_session()
        return _THREADLOCAL.session

    def url(self, name: str, additional_path: str = ""):
        """
        Create the URL for the CRUD operations.

        :param name:            Registered name of the model.
        :param additional_path: Append this to the path.
                                Must start with a forward slash.

        :return: the url of the google RESTful API endpoint to handle this model
        """
        model_metadata = lookup_metadata(name)
        return f"{self.base_url}/{model_metadata['url_part']}{additional_path}"


session_manager = SessionManager()
