from .session import session_manager
from cryptography.fernet import Fernet


def encrypt_data(data: bytes) -> bytes:
    """Encrypt bytes using the Fernet symmetric encryption algorithm.

    see https://cryptography.io/en/latest/fernet/
    """
    key = session_manager.settings.fernet_encryption_key.encode("utf8")
    fernet = Fernet(key)
    return fernet.encrypt(data)


def decrypt_data(data: bytes) -> bytes:
    """Decrypt bytes using the Fernet symmetric decryption algorithm.

    see https://cryptography.io/en/latest/fernet/
    """
    key = session_manager.settings.fernet_encryption_key.encode("utf8")
    fernet = Fernet(key)
    return fernet.decrypt(data)


def generate_fernet_key():
    """Create a new Fernet key."""
    print(Fernet.generate_key().decode("utf8"))
