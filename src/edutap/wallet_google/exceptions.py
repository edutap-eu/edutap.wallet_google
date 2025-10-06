"""Exceptions for Google Wallet API operations."""


class WalletException(Exception):
    """Base exception for Google Wallet API errors."""

    pass


class ObjectAlreadyExistsException(WalletException):
    """Raised when attempting to create an object that already exists."""

    pass


class QuotaExceededException(WalletException):
    """Raised when API quota has been exceeded."""

    pass
