from .exceptions import ObjectAlreadyExistsException
from .exceptions import QuotaExceededException
from .exceptions import WalletException
from .session import session_manager
from cryptography.fernet import Fernet

import logging


logger = logging.getLogger(__name__)


def encrypt_data(data: str) -> str:
    """Encrypt string using the Fernet symmetric encryption algorithm.

    It creates a base64 encoded string.

    The key is fetched from the settings.

    see https://cryptography.io/en/latest/fernet/
    """
    key = session_manager.settings.fernet_encryption_key.encode("utf8")
    fernet = Fernet(key)
    return fernet.encrypt(data.encode("utf8")).decode("utf8")


def decrypt_data(data: str) -> str:
    """Decrypt string using the Fernet symmetric decryption algorithm.

    It takes the base64 encoded string and returns the original value

    The key is fetched from the settings.

    see https://cryptography.io/en/latest/fernet/
    """
    key = session_manager.settings.fernet_encryption_key.encode("utf8")
    fernet = Fernet(key)
    return fernet.decrypt(data.encode("utf8")).decode("utf8")


def generate_fernet_key():
    """Create a new Fernet key."""
    print(Fernet.generate_key().decode("utf8"))


def handle_response_errors(
    response,
    operation: str,
    name: str,
    resource_id: str = "",
) -> None:
    """Handle HTTP response errors and raise appropriate exceptions.

    :param response:     HTTP response object (from requests or httpx)
    :param operation:    Operation name for error messages (e.g., "create", "read")
    :param name:         Resource name for error messages
    :param resource_id:  Resource ID for error messages
    :raises QuotaExceededException: When API quota exceeded
    :raises LookupError:            When resource not found (404)
    :raises ObjectAlreadyExistsException: When resource already exists (409)
    :raises WalletException:        For other errors
    """

    match response.status_code:
        case 200:
            return
        case 403:
            response_lower = response.text.lower()
            if "quota" in response_lower or "rate" in response_lower:
                raise QuotaExceededException(
                    f"Quota exceeded while trying to {operation} {name} {resource_id}"
                )
            raise WalletException(
                f"Access denied while trying to {operation} {name} {resource_id}: {response.text}"
            )

        case 404:
            raise LookupError(f"{name} not found: {response.text}")

        case 409:
            raise ObjectAlreadyExistsException(
                f"{name} {resource_id} already exists\n{response.text}"
            )

        case _:
            raise WalletException(f"Error: {response.status_code} - {response.text}")
