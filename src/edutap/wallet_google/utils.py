from .clientpool import client_pool
from .models.bases import Model
from cryptography.fernet import Fernet

import logging
import re
import typing


logger = logging.getLogger(__name__)


def encrypt_data(data: str) -> str:
    """Encrypt string using the Fernet symmetric encryption algorithm.

    It creates a base64 encoded string.

    The key is fetched from the settings.

    see https://cryptography.io/en/latest/fernet/
    """
    key = client_pool.settings.fernet_encryption_key.encode("utf8")
    fernet = Fernet(key)
    return fernet.encrypt(data.encode("utf8")).decode("utf8")


def decrypt_data(data: str) -> str:
    """Decrypt string using the Fernet symmetric decryption algorithm.

    It takes the base64 encoded string and returns the original value

    The key is fetched from the settings.

    see https://cryptography.io/en/latest/fernet/
    """
    key = client_pool.settings.fernet_encryption_key.encode("utf8")
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
    skip_resource_id: bool = False,
) -> tuple[str | None, str]:
    """Takes a model and data, validates it and convert to a json string.

    :param model:           Pydantic model class to use for validation.
    :param data:            Data to pass to the Google RESTful API.
                            Either a simple python data structure using built-ins,
                            or a Pydantic model instance.
    :param existing:        If True, the data is expected to be an existing object (i.e. on update).
    :param resource_id_key: Key name to fetch resource_id from.
    :param skip_resource_id: If True, skip fetching identifier and return None.
                             Also validates that the resource_id field is not set.
    :return:                Tuple of resource-id (or None if skipped) and JSON string.
    :raises ValueError:     If skip_resource_id=True but resource_id field is set.
    """
    verified_data = validate_data(model, data)
    verified_json = verified_data.model_dump_json(
        exclude_none=not existing,  # exclude None values when we create something new
        exclude_unset=True,  # exclude unset values - this are values not set explicitly by the code
        by_alias=True,
    )
    if skip_resource_id:
        # Validate that resource_id is NOT set when it should be skipped
        resource_id_value = getattr(verified_data, resource_id_key, None)
        if resource_id_value is not None:
            raise ValueError(
                f"Resource ID field '{resource_id_key}' must not be set "
                f"for this model (pass_resource_id_on_create=False)"
            )
        identifier = None
    else:
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
        # Use word boundaries to avoid false positives like "accurate", "separate"
        if re.search(r"\b(quota|rate limit|rate-limit)\b", response_lower):
            raise QuotaExceededException(
                f"Quota exceeded while trying to {operation} {name} {resource_id}"
            )
        raise WalletException(
            f"Access denied while trying to {operation} {name} {resource_id}: {response.text}"
        )

    elif response.status_code == 404:
        raise LookupError(f"{name} not found: {response.text}")

    elif response.status_code == 409:
        if allow_409:
            return
        raise ObjectAlreadyExistsException(
            f"{name} {resource_id} already exists\n{response.text}"
        )
    raise WalletException(f"Error: {response.status_code} - {response.text}")


def parse_response_json(
    response, model: type[Model], *, partial: bool = False
) -> Model:
    """Parse response JSON and return validated model instance.

    When *partial* is ``True``, a dynamic subclass is used where all required
    fields become ``Optional`` so that partial API responses (when the
    ``fields`` parameter is used) can be validated without raising for missing
    required fields.

    :param response: HTTP response object
    :param model:    Pydantic model class to validate against
    :param partial:  If True, relax required fields for partial responses
    :return:         Validated model instance
    """
    from pydantic import ValidationError

    if partial:
        from .models.bases import make_partial_model

        model = make_partial_model(model)

    logger.debug(f"RAW-Response: {response.content!r}")
    try:
        return model.model_validate_json(response.content)
    except ValidationError as e:
        logger.error(f"Validation Error: {e.errors()}")
        raise
