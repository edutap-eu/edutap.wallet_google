from .models.bases import Model
from .session import session_manager
from cryptography.fernet import Fernet

import json
import logging
import typing


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


# Shared validation utilities for API operations


def validate_data(model: type[Model], data: dict[str, typing.Any] | Model) -> Model:
    """Takes a model and data, validates it and returns a model instance.

    :param model:      Pydantic model class to use for validation.
    :param data:       Data to pass to the Google RESTful API.
                       Either a simple python data structure using built-ins,
                       or a Pydantic model instance.
    :return:           data as an instance of the given model.
    """
    if not isinstance(data, (Model)):
        return model.model_validate(data)
    if not isinstance(data, model):
        raise ValueError(
            f"Model of given data mismatches given name. Expected {model}, got {type(data)}."
        )
    return data


def validate_data_and_convert_to_json(
    model: type[Model],
    data: dict[str, typing.Any] | Model,
    *,
    existing: bool = False,
    resource_id_key: str = "id",
) -> tuple[str, str]:
    """Takes a model and data, validates it and convert to a json string.

    :param model:      Pydantic model class to use for validation.
    :param data:       Data to pass to the Google RESTful API.
                       Either a simple python data structure using built-ins,
                       or a Pydantic model instance.
    :param existing:   If True, the data is expected to be an existing object (i.e. on update).
    :return:           Tuple of resource-id and JSON string.
    """
    verified_data = validate_data(model, data)
    verified_json = verified_data.model_dump_json(
        exclude_none=not existing,  # exclude None values when we create something new
        exclude_unset=True,  # exclude unset values - this are values not set explicitly by the code
        by_alias=True,
    )
    identifier = getattr(verified_data, resource_id_key)
    return (identifier, verified_json)


# Response handling utilities


def handle_response_errors(
    response,
    operation: str,
    name: str,
    resource_id: str = "",
    allow_409: bool = False,
) -> None:
    """Handle HTTP response errors and raise appropriate exceptions.

    :param response:     HTTP response object (from requests or httpx)
    :param operation:    Operation name for error messages (e.g., "create", "read")
    :param name:         Resource name for error messages
    :param resource_id:  Resource ID for error messages
    :param allow_409:    If True, don't raise exception on 409 (for create operations)
    :raises QuotaExceededException: When API quota exceeded
    :raises LookupError:            When resource not found (404)
    :raises ObjectAlreadyExistsException: When resource already exists (409)
    :raises WalletException:        For other errors
    """
    from .exceptions import ObjectAlreadyExistsException
    from .exceptions import QuotaExceededException
    from .exceptions import WalletException

    if response.status_code == 200:
        return

    if response.status_code == 403:
        response_lower = response.text.lower()
        if "quota" in response_lower or "rate" in response_lower:
            raise QuotaExceededException(
                f"Quota exceeded while trying to {operation} {name} {resource_id}"
            )
        raise WalletException(f"Access denied: {response.text}")

    elif response.status_code == 404:
        raise LookupError(f"{name} not found: {response.text}")

    elif response.status_code == 409:
        if allow_409:
            return
        raise ObjectAlreadyExistsException(
            f"{name} {resource_id} already exists\n{response.text}"
        )

    elif response.status_code != 200:
        raise WalletException(f"Error: {response.status_code} - {response.text}")


def parse_response_json(response, model: type[Model]) -> Model:
    """Parse response JSON and return validated model instance.

    :param response: HTTP response object
    :param model:    Pydantic model class to validate against
    :return:         Validated model instance
    """
    from pydantic import ValidationError

    logger.debug(f"RAW-Response: {response.content!r}")
    try:
        return model.model_validate_json(response.content)
    except ValidationError as e:
        logger.error(f"Validation Error: {e.errors()}")
        raise
