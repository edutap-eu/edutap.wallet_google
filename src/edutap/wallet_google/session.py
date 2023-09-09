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
    def _make_session(self):
        self.base_url = os.environ.get("EDUTAP_WALLET_GOOGLE_BASE_URL", BASE_URL)
        self.batch_url = os.environ.get("EDUTAP_WALLET_GOOGLE_BATCH_URL", BATCH_URL)
        key_file_path = os.environ.get(
            "EDUTAP_WALLET_GOOGLE_APPLICATION_CREDENTIALS_FILE"
        )
        # with open(key_file_path) as credential_file:
        #     issuer_cred = json.load(credential_file)
        #     self.issuer_account = issuer_cred["client_email"]

        credentials = Credentials.from_service_account_file(
            key_file_path, scopes=SCOPES
        )
        return AuthorizedSession(credentials)

    @property
    def session(self):
        if getattr(_THREADLOCAL, "session", None) is None:
            _THREADLOCAL.session = self._make_session()
        return _THREADLOCAL.session


session_manager = SessionManager()
