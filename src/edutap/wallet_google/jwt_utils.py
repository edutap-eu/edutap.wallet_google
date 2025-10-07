"""JWT utilities for Google Wallet save links.

This module provides JWT signing and save_link generation functionality.
Uses authlib for JWT signing with RSA keys.
"""

from .credentials import credentials_manager
from .models.datatypes.jwt import JWTClaims
from .models.datatypes.jwt import JWTPayload
from .models.datatypes.jwt import Reference
from .models.passes.bases import ClassModel
from .models.passes.bases import ObjectModel
from .registry import lookup_metadata_by_model_instance
from .registry import lookup_metadata_by_model_type
from .registry import lookup_metadata_by_name
from .settings import Settings
from authlib.jose import jwt

import datetime
import logging


logger = logging.getLogger(__name__)


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

        # With sync API
        from edutap.wallet_google import api
        link = api.save_link([...])

        # With async API
        from edutap.wallet_google import api_async
        link = api_async.save_link([...])

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
