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

from .factory import new  # noqa: F401
from .models.bases import Model
from .models.datatypes.general import PaginatedResponse
from .models.datatypes.message import Message
from .models.misc import AddMessageRequest
from .registry import lookup_metadata_by_model_instance
from .registry import lookup_model_by_name
from .registry import raise_when_operation_not_allowed
from .session import session_manager
from .session import session_manager_async
from .utils import handle_response_errors
from .utils import parse_response_json
from .utils import save_link  # noqa: F401
from .utils import validate_data_and_convert_to_json
from collections.abc import AsyncGenerator
from collections.abc import Generator

import json
import logging
import typing


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


# Internal helper functions for shared logic


def _prepare_create(data: Model) -> tuple[str, str, type[Model], dict]:
    """Prepare data for create operation.

    Returns: (name, verified_json, model_type, headers)
    """
    model_metadata = lookup_metadata_by_model_instance(data)
    name = model_metadata["name"]
    raise_when_operation_not_allowed(name, "create")
    model = model_metadata["model"]
    resource_id, verified_json = validate_data_and_convert_to_json(model, data)
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
) -> tuple[type[Model], dict, bool]:
    """Prepare data for listing operation.

    Returns: (model_type, params, is_pageable)
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
    elif name.endswith("Class"):
        is_pageable = True
        if not issuer_id:
            raise ValueError("issuer_id must be given to list classes")
        params["issuerId"] = issuer_id
    elif name == "Issuer":
        is_pageable = False

    return model, params, is_pageable


def _process_listing_page(
    response_content: bytes,
    model: type[Model],
) -> tuple[list[Model], typing.Any]:
    """Process a single page of listing results.

    Returns: (validated_models, pagination_info)
    """
    data = json.loads(response_content)
    data = PaginatedResponse.model_validate(data)
    resources = data.resources
    pagination = data.pagination

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

    return validated_models, pagination


# Synchronous API


def create(
    data: Model,
    credentials: dict | None = None,
) -> Model:
    """
    Creates a Google Wallet items. `C` in CRUD.

    :param data:                          Data to pass to the Google RESTful API.
                                          A model instance, has to be a registered model.
    :param credentials:                   Optional session credentials as dict.
    :raises QuotaExceededException:       When the quota was exceeded.
    :raises ObjectAlreadyExistsException: When the id to be created already exists at Google.
    :raises WalletException:              When the response status code is not 200.
    :return:                              The created model based on the data returned by the Restful API.
    """
    name, verified_json, model, headers = _prepare_create(data)
    url = session_manager.url(name)

    with session_manager.session(credentials=credentials) as session:
        response = session.post(
            url=url,
            data=verified_json.encode("utf-8"),
            headers=headers,
        )

    handle_response_errors(response, "create", name, getattr(data, "id", "No ID"))
    return parse_response_json(response, model)


def read(
    name: str,
    resource_id: str,
    credentials: dict | None = None,
) -> Model:
    """
    Reads a Google Wallet Class or Object. `R` in CRUD.

    :param name:             Registered name of the model to use
    :param resource_id:      Identifier of the resource to read from the Google RESTful API
    :param credentials:      Optional session credentials as dict.
    :QuotaExceededException: When the quota was exceeded.
    :raises LookupError:     When the resource was not found (404).
    :raises WalletException  When the response status code is not 200 or 404.
    :return:                 The created model based on the data returned by the Restful API
    """
    (model,) = _prepare_read(name, resource_id)
    url = session_manager.url(name, f"/{resource_id}")

    with session_manager.session(credentials=credentials) as session:
        response = session.get(url=url)

    handle_response_errors(response, "read", name, resource_id)
    return parse_response_json(response, model)


def update(
    data: Model,
    *,
    partial: bool = True,
    credentials: dict | None = None,
) -> Model:
    """
    Updates a Google Wallet Class or Object. `U` in CRUD.

    :param data:                    Data to pass to the Google RESTful API.
                                    A model instance, has to be a registered model.
    :param credentials:             Optional session credentials as dict.
    :param partial:                 Whether a partial update is executed or a full replacement.
    :raises QuotaExceededException: When the quota was exceeded
    :raises LookupError:            When the resource was not found (404)
    :raises WalletException:        When the response status code is not 200 or 404
    :return:                        The created model based on the data returned by the Restful API
    """
    name, resource_id, verified_json, model = _prepare_update(data)

    with session_manager.session(credentials=credentials) as session:
        if partial:
            response = session.patch(
                url=session_manager.url(name, f"/{resource_id}"),
                data=verified_json.encode("utf-8"),
            )
        else:
            response = session.put(
                url=session_manager.url(name, f"/{resource_id}"),
                data=verified_json.encode("utf-8"),
            )

    logger.debug(verified_json.encode("utf-8"))
    handle_response_errors(response, "update", name, resource_id)
    return parse_response_json(response, model)


def message(
    name: str,
    resource_id: str,
    message: dict[str, typing.Any] | Message,
    credentials: dict | None = None,
) -> Model:
    """Sends a message to a Google Wallet Class or Object.

    :param name:                      Registered name of the model to use
    :param resource_id:               Identifier of the resource to send to
    :param message:                   Message to send.
    :param credentials:               Optional session credentials as dict.
    :raises QuotaExceededException:   When the quota was exceeded
    :raises LookupError:              When the resource was not found (404)
    :raises WalletException:          When the response status code is not 200 or 404
    :return:                          The created Model object as returned by the Restful API
    """
    model, verified_json = _prepare_message(name, message)
    url = session_manager.url(name, f"/{resource_id}/addMessage")

    with session_manager.session(credentials=credentials) as session:
        response = session.post(url=url, data=verified_json.encode("utf-8"))

    handle_response_errors(response, "send message to", name, resource_id)
    logger.debug(f"RAW-Response: {response.content!r}")
    response_data = json.loads(response.content)
    return model.model_validate(response_data.get("resource"))


def listing(
    name: str,
    *,
    resource_id: str | None = None,
    issuer_id: str | None = None,
    result_per_page: int = 0,
    next_page_token: str | None = None,
    credentials: dict | None = None,
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
    :raises QuotaExceededException: When the quota was exceeded
    :raises ValueError:             When input was invalid.
    :raises LookupError:            When the resource was not found (404)
    :raises WalletException:        When the response status code is not 200 or 404
    :return:                        Generator of the data as model-instances based on the data returned by the
                                    Restful API. When result_per_page is given, the generator will return
                                    a next_page_token after the last model-instance result.
    """
    model, params, is_pageable = _prepare_listing(name, resource_id, issuer_id)

    if is_pageable:
        if next_page_token:
            params["token"] = next_page_token
        if result_per_page:
            params["maxResults"] = f"{result_per_page}"
        else:
            params["maxResults"] = "100"

    url = session_manager.url(name)

    with session_manager.session(credentials=credentials) as session:
        while True:
            response = session.get(url=url, params=params)
            if response.status_code == 404:
                raise LookupError(f"Error 404, {name} not found: - {response.text}")
            if response.status_code != 200:
                raise Exception(f"Error: {response.status_code} - {response.text}")

            validated_models, pagination = _process_listing_page(
                response.content, model
            )

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
    credentials: dict | None = None,
) -> Model:
    """
    Creates a Google Wallet item asynchronously. `C` in CRUD.

    :param data:                          Data to pass to the Google RESTful API.
                                          A model instance, has to be a registered model.
    :param credentials:                   Optional session credentials as dict.
    :raises QuotaExceededException:       When the quota was exceeded.
    :raises ObjectAlreadyExistsException: When the id to be created already exists at Google.
    :raises WalletException:              When the response status code is not 200.
    :return:                              The created model based on the data returned by the Restful API.
    """
    name, verified_json, model, headers = _prepare_create(data)
    url = session_manager_async.url(name)

    async with session_manager_async.async_session(credentials=credentials) as session:
        response = await session.post(
            url=url,
            data=verified_json.encode("utf-8"),
            headers=headers,
        )

    handle_response_errors(response, "create", name, getattr(data, "id", "No ID"))
    return parse_response_json(response, model)


async def aread(
    name: str,
    resource_id: str,
    credentials: dict | None = None,
) -> Model:
    """
    Reads a Google Wallet Class or Object asynchronously. `R` in CRUD.

    :param name:             Registered name of the model to use
    :param resource_id:      Identifier of the resource to read from the Google RESTful API
    :param credentials:      Optional session credentials as dict.
    :QuotaExceededException: When the quota was exceeded.
    :raises LookupError:     When the resource was not found (404).
    :raises WalletException  When the response status code is not 200 or 404.
    :return:                 The created model based on the data returned by the Restful API
    """
    (model,) = _prepare_read(name, resource_id)
    url = session_manager_async.url(name, f"/{resource_id}")

    async with session_manager_async.async_session(credentials=credentials) as session:
        response = await session.get(url=url)

    handle_response_errors(response, "read", name, resource_id)
    return parse_response_json(response, model)


async def aupdate(
    data: Model,
    *,
    partial: bool = True,
    credentials: dict | None = None,
) -> Model:
    """
    Updates a Google Wallet Class or Object asynchronously. `U` in CRUD.

    :param data:                    Data to pass to the Google RESTful API.
                                    A model instance, has to be a registered model.
    :param credentials:             Optional session credentials as dict.
    :param partial:                 Whether a partial update is executed or a full replacement.
    :raises QuotaExceededException: When the quota was exceeded
    :raises LookupError:            When the resource was not found (404)
    :raises WalletException:        When the response status code is not 200 or 404
    :return:                        The created model based on the data returned by the Restful API
    """
    name, resource_id, verified_json, model = _prepare_update(data)

    async with session_manager_async.async_session(credentials=credentials) as session:
        if partial:
            response = await session.patch(
                url=session_manager_async.url(name, f"/{resource_id}"),
                data=verified_json.encode("utf-8"),
            )
        else:
            response = await session.put(
                url=session_manager_async.url(name, f"/{resource_id}"),
                data=verified_json.encode("utf-8"),
            )

    logger.debug(verified_json.encode("utf-8"))
    handle_response_errors(response, "update", name, resource_id)
    return parse_response_json(response, model)


async def amessage(
    name: str,
    resource_id: str,
    message: dict[str, typing.Any] | Message,
    credentials: dict | None = None,
) -> Model:
    """Sends a message to a Google Wallet Class or Object asynchronously.

    :param name:                      Registered name of the model to use
    :param resource_id:               Identifier of the resource to send to
    :param message:                   Message to send.
    :param credentials:               Optional session credentials as dict.
    :raises QuotaExceededException:   When the quota was exceeded
    :raises LookupError:              When the resource was not found (404)
    :raises WalletException:          When the response status code is not 200 or 404
    :return:                          The created Model object as returned by the Restful API
    """
    model, verified_json = _prepare_message(name, message)
    url = session_manager_async.url(name, f"/{resource_id}/addMessage")

    async with session_manager_async.async_session(credentials=credentials) as session:
        response = await session.post(url=url, data=verified_json.encode("utf-8"))

    handle_response_errors(response, "send message to", name, resource_id)
    logger.debug(f"RAW-Response: {response.content!r}")
    response_data = json.loads(response.content)
    return model.model_validate(response_data.get("resource"))


async def alisting(
    name: str,
    *,
    resource_id: str | None = None,
    issuer_id: str | None = None,
    result_per_page: int = 0,
    next_page_token: str | None = None,
    credentials: dict | None = None,
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
    :raises QuotaExceededException: When the quota was exceeded
    :raises ValueError:             When input was invalid.
    :raises LookupError:            When the resource was not found (404)
    :raises WalletException:        When the response status code is not 200 or 404
    :return:                        AsyncGenerator of the data as model-instances based on the data returned by the
                                    Restful API. When result_per_page is given, the generator will return
                                    a next_page_token after the last model-instance result.
    """
    model, params, is_pageable = _prepare_listing(name, resource_id, issuer_id)

    if is_pageable:
        if next_page_token:
            params["token"] = next_page_token
        if result_per_page:
            params["maxResults"] = f"{result_per_page}"
        else:
            params["maxResults"] = "100"

    url = session_manager_async.url(name)

    async with session_manager_async.async_session(credentials=credentials) as session:
        while True:
            response = await session.get(url=url, params=params)
            # Use shared error handling for consistent exception types
            if name.endswith("Object"):
                resource_identifier = resource_id if resource_id else ""
            else:
                resource_identifier = issuer_id if issuer_id else ""
            handle_response_errors(response, "list", name, resource_identifier)

            validated_models, pagination = _process_listing_page(
                response.content, model
            )

            for validated_model in validated_models:
                yield validated_model

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
