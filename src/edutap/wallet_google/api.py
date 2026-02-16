"""Google Wallet API for both synchronous and asynchronous operations.

This module provides the complete API for Google Wallet pass management.
It includes both sync and async versions of all CRUD operations.

**Naming Convention:**
- Synchronous functions: `create()`, `read()`, `update()`, `message()`, `listing()`
- Asynchronous functions: `acreate()`, `aread()`, `aupdate()`, `amessage()`, `alisting()`
- Shared functions (work with both): `new()`, `save_link()`

**Usage:**

Synchronous API:
```python
from edutap.wallet_google import api

my_pass = api.new("GenericObject", {...})
result = api.create(my_pass)
link = api.save_link([my_pass])
```

Asynchronous API:
```python
from edutap.wallet_google import api

my_pass = api.new("GenericObject", {...})
result = await api.acreate(my_pass)
link = api.save_link([my_pass])  # save_link is sync, not awaited
```
"""

from collections.abc import AsyncGenerator, Generator
import datetime
import json
import logging
import typing

from authlib.jose import jwt

from .clientpool import client_pool
from .credentials import credentials_manager
from .models.bases import Model, make_partial_model
from .models.datatypes.general import PaginatedResponse, Pagination
from .models.datatypes.jwt import JWTClaims, JWTPayload
from .models.datatypes.message import Message
from .models.misc import AddMessageRequest
from .models.passes.bases import ClassModel, ObjectModel, Reference
from .registry import (
    lookup_metadata_by_model_instance,
    lookup_metadata_by_model_type,
    lookup_metadata_by_name,
    lookup_model_by_name,
    raise_when_operation_not_allowed,
    validate_fields_for_name,
)
from .utils import (
    handle_response_errors,
    parse_response_json,
    validate_data,
    validate_data_and_convert_to_json,
)

logger = logging.getLogger(__name__)


__all__ = [
    "new",
    "save_link",
    "create",
    "read",
    "update",
    "message",
    "listing",
    "acreate",
    "aread",
    "aupdate",
    "amessage",
    "alisting",
]


# Shared API functions


def new(
    name: str,
    data: dict[str, typing.Any] | None = None,
):
    """
    Factors a new registered Google Wallet Model by name, based on the given data.

    :param name:       Registered name of the model to use
    :param data:       Data to initialize the model with.
                       A simple JSON compatible Python data structure using built-ins.
    :raises Exception: When the data does not validate.
    :return:           The created model instance.
    """
    if data is None:
        data = {}
    model = lookup_model_by_name(name)
    return validate_data(model, data)


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
    origins: list[str] | None = None,
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
    if origins is None:
        origins = []
    if credentials is None:
        credentials = credentials_manager.credentials_from_file()

    settings = client_pool.settings
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


# Internal helper functions for CRUD operations


def _validate_partial_response_fields(
    fields: list[str],
    name: str,
) -> bool:
    """Validate that all fields in the list are valid field names for the given model.

    :param fields:     List of field names to validate.
    :param name:       Registered name of the Pydantic model class to validate against.
    :return:           True if all provided fields are valid for the model;
                       False if any field is invalid or if no fields are provided.
    """
    if fields:
        # Accept fields that are prefixed with 'resource.' by stripping the
        # prefix for validation but keeping the original field names when
        # building the HTTP params (Google supports nested selectors like
        # 'resource.id').
        stripped = [
            f.split(".", 1)[1] if f.startswith("resource.") else f for f in fields
        ]
        valid_stripped, _ = validate_fields_for_name(name, stripped)
        if not valid_stripped:
            return False
        return True
    return False


def _prepare_create(data: Model) -> tuple[str, str, type[Model], dict]:
    """Prepare data for create operation.

    Returns: (name, verified_json, model_type, headers)
    """
    model_metadata = lookup_metadata_by_model_instance(data)
    name = model_metadata["name"]
    raise_when_operation_not_allowed(name, "create")
    model = model_metadata["model"]

    # Check if resource_id should be skipped (not passed on create)
    skip_resource_id = not model_metadata.get("pass_resource_id_on_create", True)
    resource_id_key = model_metadata.get("resource_id", "id")

    _, verified_json = validate_data_and_convert_to_json(
        model, data, skip_resource_id=skip_resource_id, resource_id_key=resource_id_key
    )
    headers = {"Content-Type": "application/json"}
    return name, verified_json, model, headers


def _prepare_read(name: str, resource_id: str) -> tuple[type[Model]]:
    """Prepare data for read operation.

    Returns: (model_type,)
    """
    raise_when_operation_not_allowed(name, "read")
    model = lookup_model_by_name(name)
    return (model,)


def _prepare_update(
    data: Model,
) -> tuple[str, str, str, type[Model]]:
    """Prepare data for update operation.

    Returns: (name, resource_id, verified_json, model_type)
    """
    model_metadata = lookup_metadata_by_model_instance(data)
    name = model_metadata["name"]
    raise_when_operation_not_allowed(name, "update")
    model = model_metadata["model"]
    resource_id, verified_json = validate_data_and_convert_to_json(
        model, data, existing=True, resource_id_key=model_metadata["resource_id"]
    )
    assert resource_id is not None, "resource_id is required for update"
    return name, resource_id, verified_json, model


def _prepare_message(
    name: str,
    message: dict[str, typing.Any] | Message,
) -> tuple[type[Model], str]:
    """Prepare data for message operation.

    Returns: (model_type, verified_json)
    """
    raise_when_operation_not_allowed(name, "message")
    model = lookup_model_by_name(name)

    if not isinstance(message, Message):
        message_validated = Message.model_validate(message)
    else:
        message_validated = message

    add_message = AddMessageRequest(message=message_validated)
    verified_json = add_message.model_dump_json(exclude_none=True)
    return model, verified_json


def _prepare_listing(
    name: str,
    resource_id: str | None,
    issuer_id: str | None,
) -> tuple[type[Model], dict, bool, str]:
    """Prepare data for listing operation.

    Returns: (model_type, params, is_pageable, resource_identifier)
    """
    raise_when_operation_not_allowed(name, "list")
    if resource_id and issuer_id:
        raise ValueError("resource_id and issuer_id are mutually exclusive")

    model = lookup_model_by_name(name)

    params = {}
    is_pageable = False
    if name.endswith("Object"):
        is_pageable = True
        if not resource_id:
            raise ValueError("resource_id of a class must be given to list its objects")
        params["classId"] = resource_id
        resource_identifier = resource_id if resource_id else ""
    elif name.endswith("Class"):
        is_pageable = True
        if not issuer_id:
            raise ValueError("issuer_id must be given to list classes")
        params["issuerId"] = issuer_id
        resource_identifier = issuer_id if issuer_id else ""
    elif name == "Issuer":
        is_pageable = False
        resource_identifier = ""
    else:
        resource_identifier = ""

    return model, params, is_pageable, resource_identifier


def _process_listing_page(
    response_content: bytes,
    model: type[Model],
) -> list[Model]:
    """Process a single page of listing results.

    Returns: list of validated models
    """
    paginated_response = PaginatedResponse.model_validate_json(response_content)
    pagination = paginated_response.pagination
    resources = paginated_response.resources

    validated_models = []
    if not resources:
        logger.warning("Response does not contain 'resources'")
        if pagination and pagination.resultsPerPage == 0:
            logger.warning(
                "No results per page set, this might be an error in the API response."
            )
    else:
        for count, record in enumerate(resources):
            try:
                validated_models.append(model.model_validate(record))
            except Exception:
                logger.exception(f"Error validating record {count}:\n{record}")
                raise

    return validated_models


def _setup_pagination_params(
    is_pageable: bool,
    result_per_page: int,
    next_page_token: str | None,
) -> dict:
    """Setup pagination parameters for listing operations.

    Returns: params dict with pagination settings
    """
    params = {}
    if is_pageable:
        if next_page_token:
            params["token"] = next_page_token
        if result_per_page:
            params["maxResults"] = f"{result_per_page}"
        else:
            params["maxResults"] = "100"
    return params


# Synchronous API


def create(
    data: Model,
    *,
    credentials: dict | None = None,
    fields: list[str] | None = None,
) -> Model:
    """
    Creates a Google Wallet items. `C` in CRUD.

    :param data:                          Data to pass to the Google RESTful API.
                                          A model instance, has to be a registered model.
    :param credentials:                   Optional session credentials as dict.
    :param fields:                        Optional list of fields to include in the response for partial responses.
    :raises QuotaExceededException:       When the quota was exceeded.
    :raises ObjectAlreadyExistsException: When the id to be created already exists at Google.
    :raises WalletException:              When the response status code is not 200.
    :return:                              The created model instance.
    """
    name, verified_json, model, headers = _prepare_create(data)
    url = client_pool.url(name)
    params: dict[str, str] | None = None

    if fields:
        if _validate_partial_response_fields(fields, name):
            params = {"fields": ",".join(fields)}

    client = client_pool.client(credentials=credentials)
    response = client.post(
        url=url,
        data=verified_json.encode("utf-8"),
        headers=headers,
        params=params,
    )

    handle_response_errors(response, "create", name, getattr(data, "id", "No ID"))
    if params is not None:
        return parse_response_json(response, model, partial=True)
    return parse_response_json(response, model)


def read(
    name: str,
    resource_id: str,
    *,
    credentials: dict | None = None,
    fields: list[str] | None = None,
) -> Model:
    """
    Reads a Google Wallet Class or Object. `R` in CRUD.

    :param name:             Registered name of the model to use
    :param resource_id:      Identifier of the resource to read from the Google RESTful API
    :param credentials:      Optional session credentials as dict.
    :param fields:           Optional list of fields to include in the response for partial responses.
    :QuotaExceededException: When the quota was exceeded.
    :raises LookupError:     When the resource was not found (404).
    :raises WalletException  When the response status code is not 200 or 404.
    :return:                 The retrieved model instance.
    """
    (model,) = _prepare_read(name, resource_id)
    url = client_pool.url(name, f"/{resource_id}")
    params: dict[str, str] | None = None
    if fields:
        if _validate_partial_response_fields(fields, name):
            params = {"fields": ",".join(fields)}

    client = client_pool.client(credentials=credentials)
    response = client.get(url=url, params=params)

    handle_response_errors(response, "read", name, resource_id)
    if params is not None:
        return parse_response_json(response, model, partial=True)
    return parse_response_json(response, model)


def update(
    data: Model,
    *,
    credentials: dict | None = None,
    fields: list[str] | None = None,
    partial: bool = True,
) -> Model:
    """
    Updates a Google Wallet Class or Object. `U` in CRUD.

    :param data:                    Data to pass to the Google RESTful API.
                                    A model instance, has to be a registered model.
    :param credentials:             Optional session credentials as dict.
    :param fields:                  Optional list of fields to include in the response for partial responses.
    :param partial:                 Optional Flag, whether a partial update is executed or a full replacement.
    :raises QuotaExceededException: When the quota was exceeded
    :raises LookupError:            When the resource was not found (404)
    :raises WalletException:        When the response status code is not 200 or 404
    :return:                        The updated model instance.
    """
    name, resource_id, verified_json, model = _prepare_update(data)
    params: dict[str, str] | None = None
    if fields:
        if _validate_partial_response_fields(fields, name):
            params = {"fields": ",".join(fields)}

    session = client_pool.client(credentials=credentials)
    if partial:
        response = session.patch(
            url=client_pool.url(name, f"/{resource_id}"),
            data=verified_json.encode("utf-8"),
            params=params,
        )
    else:
        response = session.put(
            url=client_pool.url(name, f"/{resource_id}"),
            data=verified_json.encode("utf-8"),
            params=params,
        )

    logger.debug(verified_json.encode("utf-8"))
    handle_response_errors(response, "update", name, resource_id)
    if params is not None:
        return parse_response_json(response, model, partial=True)
    return parse_response_json(response, model)


def message(
    name: str,
    resource_id: str,
    message: dict[str, typing.Any] | Message,
    *,
    credentials: dict | None = None,
    fields: list[str] | None = None,
) -> Model:
    """Sends a message to a Google Wallet Class or Object.

    :param name:                      Registered name of the model to use
    :param resource_id:               Identifier of the resource to send to
    :param message:                   Message to send.
    :param credentials:               Optional session credentials as dict.
    :param fields:                    Optional list of fields to include in the response for partial responses.
    :raises QuotaExceededException:   When the quota was exceeded
    :raises LookupError:              When the resource was not found (404)
    :raises WalletException:          When the response status code is not 200 or 404
    :return:                          The created model based on the data, or a dict with the partial requested response data returned by the Restful API.
    """
    model, verified_json = _prepare_message(name, message)
    url = client_pool.url(name, f"/{resource_id}/addMessage")
    params: dict[str, str] | None = None
    if fields:
        if _validate_partial_response_fields(fields, name):
            params = {"fields": ",".join(fields)}

    client = client_pool.client(credentials=credentials)
    response = client.post(url=url, data=verified_json.encode("utf-8"), params=params)

    handle_response_errors(response, "send message to", name, resource_id)
    logger.debug(f"RAW-Response: {response.content!r}")
    resource_data = json.loads(response.content)["resource"]
    if params is not None:
        partial_model = make_partial_model(model)
        return partial_model.model_validate(resource_data)
    return model.model_validate(resource_data)


def listing(
    name: str,
    *,
    resource_id: str | None = None,
    issuer_id: str | None = None,
    result_per_page: int = 0,
    next_page_token: str | None = None,
    credentials: dict | None = None,
    fields: list[str] | None = None,
) -> Generator[Model | str, None, None]:
    """Lists wallet related resources.

    It is possible to list all classes of an issuer. Parameter 'name' has to end with 'Class',
    all objects of a registered object type by it's classes resource id,
    Parameter 'name' has to end with 'Object'.
    To get all issuers, parameter 'name' has to be 'Issuer' and no further parameters are allowed.

    :param name:                    Registered name to base the listing on.
    :param resource_id:             Id of the class to list objects of.
                                    Only for object listings`
                                    Mutually exclusive with issuer_id.
    :param issuer_id:               Identifier of the issuer to list classes of.
                                    Only for class listings.
                                    If no resource_id is given and issuer_id is None, it will
                                    be fetched from the environment variable EDUTAP_WALLET_GOOGLE_ISSUER_ID.
                                    Mutually exclusive with resource_id.
    :param result_per_page:         Number of results per page to fetch.
                                    If omitted all results will be fetched and provided by the generator.
    :param next_page_token:         Token to get the next page of results.
    :param credentials:             Optional session credentials as dict.
    :param fields:                  Optional list of fields to include in the response for partial responses.
    :raises QuotaExceededException: When the quota was exceeded
    :raises ValueError:             When input was invalid.
    :raises LookupError:            When the resource was not found (404)
    :raises WalletException:        When the response status code is not 200 or 404
    :return:                        Generator of model instances based on the data returned by the
                                    Restful API. When result_per_page is given, the generator will return
                                    a next_page_token after the last model-instance result.
    """
    model, params, is_pageable, resource_identifier = _prepare_listing(
        name, resource_id, issuer_id
    )
    if fields:
        if _validate_partial_response_fields(fields, name):
            params["fields"] = ",".join(fields)

    # Setup pagination parameters
    pagination_params = _setup_pagination_params(
        is_pageable, result_per_page, next_page_token
    )
    params.update(pagination_params)

    url = client_pool.url(name)

    client = client_pool.client(credentials=credentials)
    while True:
        response = client.get(url=url, params=params)
        handle_response_errors(response, "list", name, resource_identifier)
        paginated_response = PaginatedResponse.model_validate_json(response.content)
        pagination: Pagination | None = paginated_response.pagination

        if "fields" in params:
            partial_model = make_partial_model(model)
            resources = paginated_response.resources
            if resources:
                yield from (partial_model.model_validate(r) for r in resources)
        else:
            validated_models = _process_listing_page(response.content, model)
            yield from validated_models

        if not is_pageable or not pagination:
            break
        if result_per_page > 0:
            if pagination.nextPageToken:
                yield pagination.nextPageToken
                break
        else:
            if pagination.nextPageToken:
                params["token"] = pagination.nextPageToken
                continue
        break
    return


# Asynchronous API


async def acreate(
    data: Model,
    *,
    credentials: dict | None = None,
    fields: list[str] | None = None,
) -> Model:
    """
    Creates a Google Wallet item asynchronously. `C` in CRUD.

    :param data:                          Data to pass to the Google RESTful API.
                                          A model instance, has to be a registered model.
    :param credentials:                   Optional session credentials as dict.
    :param fields:                        Optional list of fields to include in the response for partial responses.
    :raises QuotaExceededException:       When the quota was exceeded.
    :raises ObjectAlreadyExistsException: When the id to be created already exists at Google.
    :raises WalletException:              When the response status code is not 200.
    :return:                              The created model instance.
    """
    name, verified_json, model, headers = _prepare_create(data)
    url = client_pool.url(name)
    params: dict[str, str] | None = None
    if fields:
        if _validate_partial_response_fields(fields, name):
            params = {"fields": ",".join(fields)}

    client = client_pool.async_client(credentials=credentials)
    response = await client.post(
        url=url,
        data=verified_json.encode("utf-8"),
        headers=headers,
        params=params,
    )

    handle_response_errors(response, "create", name, getattr(data, "id", "No ID"))
    if params is not None:
        return parse_response_json(response, model, partial=True)
    return parse_response_json(response, model)


async def aread(
    name: str,
    resource_id: str,
    *,
    credentials: dict | None = None,
    fields: list[str] | None = None,
) -> Model:
    """
    Reads a Google Wallet Class or Object asynchronously. `R` in CRUD.

    :param name:             Registered name of the model to use
    :param resource_id:      Identifier of the resource to read from the Google RESTful API
    :param credentials:      Optional session credentials as dict.
    :param fields:           Optional list of fields to include in the response for partial responses.
    :QuotaExceededException: When the quota was exceeded.
    :raises LookupError:     When the resource was not found (404).
    :raises WalletException  When the response status code is not 200 or 404.
    :return:                 The retrieved model instance.
    """
    (model,) = _prepare_read(name, resource_id)
    url = client_pool.url(name, f"/{resource_id}")
    params: dict[str, str] | None = None
    if fields:
        if _validate_partial_response_fields(fields, name):
            params = {"fields": ",".join(fields)}

    client = client_pool.async_client(credentials=credentials)
    response = await client.get(url=url, params=params)

    handle_response_errors(response, "read", name, resource_id)
    if params is not None:
        return parse_response_json(response, model, partial=True)
    return parse_response_json(response, model)


async def aupdate(
    data: Model,
    *,
    credentials: dict | None = None,
    fields: list[str] | None = None,
    partial: bool = True,
) -> Model:
    """
    Updates a Google Wallet Class or Object asynchronously. `U` in CRUD.

    :param data:                    Data to pass to the Google RESTful API.
                                    A model instance, has to be a registered model.
    :param credentials:             Optional session credentials as dict.
    :param fields:                  Optional list of fields to include in the response for partial responses.
    :param partial:                 Optional boolean indicating whether a partial update is executed or a full replacement.
    :raises QuotaExceededException: When the quota was exceeded
    :raises LookupError:            When the resource was not found (404)
    :raises WalletException:        When the response status code is not 200 or 404
    :return:                        The updated model instance.
    """
    name, resource_id, verified_json, model = _prepare_update(data)
    params: dict[str, str] | None = None
    if fields:
        if _validate_partial_response_fields(fields, name):
            params = {"fields": ",".join(fields)}

    session = client_pool.async_client(credentials=credentials)
    if partial:
        response = await session.patch(
            url=client_pool.url(name, f"/{resource_id}"),
            data=verified_json.encode("utf-8"),
            params=params,
        )
    else:
        response = await session.put(
            url=client_pool.url(name, f"/{resource_id}"),
            data=verified_json.encode("utf-8"),
            params=params,
        )

    logger.debug(verified_json.encode("utf-8"))
    handle_response_errors(response, "update", name, resource_id)
    if params is not None:
        return parse_response_json(response, model, partial=True)
    return parse_response_json(response, model)


async def amessage(
    name: str,
    resource_id: str,
    message: dict[str, typing.Any] | Message,
    *,
    credentials: dict | None = None,
    fields: list[str] | None = None,
) -> Model:
    """Sends a message to a Google Wallet Class or Object asynchronously.

    :param name:                      Registered name of the model to use
    :param resource_id:               Identifier of the resource to send to
    :param message:                   Message to send.
    :param credentials:               Optional session credentials as dict.
    :param fields:                    Optional list of fields to include in the response for partial responses.
    :raises QuotaExceededException:   When the quota was exceeded
    :raises LookupError:              When the resource was not found (404)
    :raises WalletException:          When the response status code is not 200 or 404
    :return:                          The model instance.
    """
    model, verified_json = _prepare_message(name, message)
    url = client_pool.url(name, f"/{resource_id}/addMessage")
    params: dict[str, str] | None = None
    if fields:
        if _validate_partial_response_fields(fields, name):
            params = {"fields": ",".join(fields)}

    client = client_pool.async_client(credentials=credentials)
    response = await client.post(
        url=url, data=verified_json.encode("utf-8"), params=params
    )

    handle_response_errors(response, "send message to", name, resource_id)
    logger.debug(f"RAW-Response: {response.content!r}")
    resource_data = json.loads(response.content)["resource"]
    if params is not None:
        partial_model = make_partial_model(model)
        return partial_model.model_validate(resource_data)
    return model.model_validate(resource_data)


async def alisting(
    name: str,
    *,
    resource_id: str | None = None,
    issuer_id: str | None = None,
    result_per_page: int = 0,
    next_page_token: str | None = None,
    credentials: dict | None = None,
    fields: list[str] | None = None,
) -> AsyncGenerator[Model | str, None]:
    """Lists wallet related resources asynchronously.

    It is possible to list all classes of an issuer. Parameter 'name' has to end with 'Class',
    all objects of a registered object type by it's classes resource id,
    Parameter 'name' has to end with 'Object'.
    To get all issuers, parameter 'name' has to be 'Issuer' and no further parameters are allowed.

    :param name:                    Registered name to base the listing on.
    :param resource_id:             Id of the class to list objects of.
                                    Only for object listings`
                                    Mutually exclusive with issuer_id.
    :param issuer_id:               Identifier of the issuer to list classes of.
                                    Only for class listings.
                                    If no resource_id is given and issuer_id is None, it will
                                    be fetched from the environment variable EDUTAP_WALLET_GOOGLE_ISSUER_ID.
                                    Mutually exclusive with resource_id.
    :param result_per_page:         Number of results per page to fetch.
                                    If omitted all results will be fetched and provided by the generator.
    :param next_page_token:         Token to get the next page of results.
    :param credentials:             Optional session credentials as dict.
    :param fields:                  Optional list of fields to include in the response for partial responses.
    :raises QuotaExceededException: When the quota was exceeded
    :raises ValueError:             When input was invalid.
    :raises LookupError:            When the resource was not found (404)
    :raises WalletException:        When the response status code is not 200 or 404
    :return:                        AsyncGenerator of the data as model-instances based on the data returned by the
                                    Restful API. When result_per_page is given, the generator will return
                                    a next_page_token after the last model-instance result.
    """
    model, params, is_pageable, resource_identifier = _prepare_listing(
        name, resource_id, issuer_id
    )
    if fields:
        if _validate_partial_response_fields(fields, name):
            params["fields"] = ",".join(fields)

    # Setup pagination parameters
    pagination_params = _setup_pagination_params(
        is_pageable, result_per_page, next_page_token
    )
    params.update(pagination_params)

    url = client_pool.url(name)

    client = client_pool.async_client(credentials=credentials)
    while True:
        response = await client.get(url=url, params=params)
        handle_response_errors(response, "list", name, resource_identifier)
        paginated_response = PaginatedResponse.model_validate_json(response.content)
        pagination: Pagination | None = paginated_response.pagination

        if "fields" in params:
            partial_model = make_partial_model(model)
            resources = paginated_response.resources
            if resources:
                for resource in resources:
                    yield partial_model.model_validate(resource)
        else:
            validated_models = _process_listing_page(response.content, model)
            for resource in validated_models:
                yield resource

        if not is_pageable or not pagination:
            break
        if result_per_page > 0:
            if pagination.nextPageToken:
                yield pagination.nextPageToken
                break
        else:
            if pagination.nextPageToken:
                params["token"] = pagination.nextPageToken
                continue
        break
    return
