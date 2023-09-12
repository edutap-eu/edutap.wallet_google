from .registry import lookup_metadata
from dotenv import load_dotenv
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.service_account import Credentials

import os
import threading


load_dotenv()

_THREADLOCAL = threading.local()

BASE_URL = "https://walletobjects.googleapis.com/walletobjects/v1"
BATCH_URL = "https://walletobjects.googleapis.com/batch"
SCOPES = ["https://www.googleapis.com/auth/wallet_object.issuer"]


class SessionManager:
    def __init__(self):
        self.base_url = os.environ.get("EDUTAP_WALLET_GOOGLE_BASE_URL", BASE_URL)
        self.batch_url = os.environ.get("EDUTAP_WALLET_GOOGLE_BATCH_URL", BATCH_URL)

    def _make_session(self):
        key_file_path = os.environ.get(
            "EDUTAP_WALLET_GOOGLE_APPLICATION_CREDENTIALS_FILE"
        )

        credentials = Credentials.from_service_account_file(
            key_file_path, scopes=SCOPES
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
