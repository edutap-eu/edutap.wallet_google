from .session import session_manager
from cryptography.fernet import Fernet


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
