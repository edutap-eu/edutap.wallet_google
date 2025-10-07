from .credentials import credentials_manager
from .models.bases import Model
from .models.datatypes.jwt import JWTClaims
from .models.datatypes.jwt import JWTPayload
from .models.datatypes.jwt import Reference
from .models.passes.bases import ClassModel
from .models.passes.bases import ObjectModel
from .registry import lookup_metadata_by_model_instance
from .registry import lookup_metadata_by_model_type
from .registry import lookup_metadata_by_name
from .session import session_manager
from .settings import Settings
from authlib.jose import jwt
from cryptography.fernet import Fernet

import datetime
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


# JWT utilities for save_link generation


def _create_payload(models: list[ClassModel | ObjectModel | Reference]) -> JWTPayload:
    """Creates a payload for the JWT."""
    payload = JWTPayload()

    for model in models:
        if isinstance(model, Reference):
            if model.model_name is not None:
                name = lookup_metadata_by_name(model.model_name)["plural"]
            elif model.model_type is not None:
                name = lookup_metadata_by_model_type(model.model_type)["plural"]
        else:
            name = lookup_metadata_by_model_instance(model)["plural"]
        if getattr(payload, name) is None:
            setattr(payload, name, [])
        getattr(payload, name).append(model)
    return payload


def _convert_str_or_datetime_to_str(value: str | datetime.datetime) -> str:
    """convert and check the value to be a valid string for the JWT claim timestamps"""
    if isinstance(value, datetime.datetime):
        return str(int(value.timestamp()))
    if value == "":
        return value
    if not value.isdecimal():
        raise ValueError("string must be a decimal")
    if int(value) < 0:
        raise ValueError("string must be an int >= 0 number")
    if int(value) > 2**32:
        raise ValueError("string must be an int < 2**32 number")
    return value


def _create_claims(
    issuer: str,
    origins: list[str],
    models: list[ClassModel | ObjectModel | Reference],
    iat: str | datetime.datetime,
    exp: str | datetime.datetime,
) -> JWTClaims:
    """Creates a JWTClaims instance based on the given issuer, origins and models."""
    return JWTClaims(
        iss=issuer,
        iat=_convert_str_or_datetime_to_str(iat),
        exp=_convert_str_or_datetime_to_str(exp),
        origins=origins,
        payload=_create_payload(models),
    )


def save_link(
    models: list[ClassModel | ObjectModel | Reference],
    *,
    origins: list[str] = [],
    iat: str | datetime.datetime = "",
    exp: str | datetime.datetime = "",
    credentials: dict | None = None,
) -> str:
    """
    Creates a link to save a Google Wallet Object to the wallet on the device.

    Besides the capability to save an object to the wallet, it is also able create classes on-the-fly.

    More information about the construction of the save_link can be found here:

    - https://developers.google.com/wallet/reference/rest/v1/jwt
    - https://developers.google.com/wallet/generic/web
    - https://developers.google.com/wallet/generic/use-cases/jwt

    This function uses authlib for JWT signing with RSA keys.
    It can be used with both sync and async APIs:

    .. code-block:: python

        from edutap.wallet_google import api
        link = api.save_link([...])

    :param models:      List of ObjectModels or ClassModels to save.
                        A resource can be an ObjectReference instance too.
    :param origins:     List of domains to approve for JWT saving functionality.
                        The Google Wallet API button will not render when the origins field is not defined.
                        You could potentially get an "Load denied by X-Frame-Options" or "Refused to display"
                        messages in the browser console when the origins field is not defined.
    :param: iat:        Issued At Time. The time when the JWT was issued.
    :param: exp:        Expiration Time. The time when the JWT expires.
    :param credentials: Optional session credentials as dict.
    :return:            Link with JWT to save the resources to the wallet.
    """
    if credentials is None:
        credentials = credentials_manager.credentials_from_file()

    settings = Settings()
    claims = _create_claims(
        credentials["client_email"],
        origins,
        models,
        iat=iat,
        exp=exp,
    )
    logger.debug(
        claims.model_dump_json(
            indent=2,
            exclude_unset=False,
            exclude_defaults=False,
            exclude_none=True,
        )
    )

    # Use authlib to sign JWT with RS256
    header = {
        "alg": "RS256",
        "typ": "JWT",
        "kid": credentials["private_key_id"],
    }
    payload = claims.model_dump(
        mode="json",
        exclude_unset=False,
        exclude_defaults=False,
        exclude_none=True,
    )

    # authlib's jwt.encode returns bytes
    jwt_bytes = jwt.encode(header, payload, credentials["private_key"])
    jwt_string = jwt_bytes.decode("utf-8")

    logger.debug(jwt_string)
    if (jwt_len := len(jwt_string)) >= 1800:
        logger.debug(
            f"JWT-Length: {jwt_len} is larger than recommended 1800 bytes",
        )
    return f"{settings.save_url}/{jwt_string}"
