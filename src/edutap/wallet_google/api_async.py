"""Async API for Google Wallet operations using httpx.

This module provides async versions of all Google Wallet API operations.
Use these functions when you need non-blocking I/O, such as in async web frameworks
like FastAPI, or when making multiple concurrent API calls.

For synchronous code, use the regular `api` module instead.

Note: save_link() is a permanent part of both sync and async APIs.
"""

from .exceptions import ObjectAlreadyExistsException
from .factory import new  # noqa: F401
from .jwt_utils import save_link  # noqa: F401
from .models.bases import Model
from .models.datatypes.general import PaginatedResponse
from .models.datatypes.message import Message
from .models.misc import AddMessageRequest
from .registry import lookup_metadata_by_model_instance
from .registry import lookup_model_by_name
from .registry import raise_when_operation_not_allowed
from .session_async import session_manager_async
from .utils import handle_response_errors
from .utils import parse_response_json
from .utils import validate_data_and_convert_to_json
from collections.abc import AsyncGenerator

import json
import logging
import typing


logger = logging.getLogger(__name__)


async def create(
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
    model_metadata = lookup_metadata_by_model_instance(data)
    name = model_metadata["name"]
    raise_when_operation_not_allowed(name, "create")
    model = model_metadata["model"]
    resource_id, verified_json = validate_data_and_convert_to_json(model, data)
    url = session_manager_async.url(name)
    headers = {"Content-Type": "application/json"}

    async with session_manager_async.session(credentials=credentials) as session:
        response = await session.post(
            url=url,
            data=verified_json.encode("utf-8"),
            headers=headers,
        )

    handle_response_errors(
        response, "create", name, getattr(data, "id", "No ID"), allow_409=True
    )
    if response.status_code == 409:
        raise ObjectAlreadyExistsException(
            f"{name} {getattr(data, 'id', 'No ID')} already exists\n{response.text}"
        )
    return parse_response_json(response, model)


async def read(
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
    raise_when_operation_not_allowed(name, "read")
    url = session_manager_async.url(name, f"/{resource_id}")

    async with session_manager_async.session(credentials=credentials) as session:
        response = await session.get(url=url)

    handle_response_errors(response, "read", name, resource_id)
    model = lookup_model_by_name(name)
    return parse_response_json(response, model)


async def update(
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
    model_metadata = lookup_metadata_by_model_instance(data)
    name = model_metadata["name"]
    raise_when_operation_not_allowed(name, "update")
    model = model_metadata["model"]
    resource_id, verified_json = validate_data_and_convert_to_json(
        model, data, existing=True, resource_id_key=model_metadata["resource_id"]
    )

    async with session_manager_async.session(credentials=credentials) as session:
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


async def message(
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
    raise_when_operation_not_allowed(name, "message")
    model = lookup_model_by_name(name)

    if not isinstance(message, Message):
        message_validated = Message.model_validate(message)
    else:
        message_validated = message

    add_message = AddMessageRequest(message=message_validated)
    verified_json = add_message.model_dump_json(
        exclude_none=True,
    )
    url = session_manager_async.url(name, f"/{resource_id}/addMessage")

    async with session_manager_async.session(credentials=credentials) as session:
        response = await session.post(url=url, data=verified_json.encode("utf-8"))

    handle_response_errors(response, "send message to", name, resource_id)
    logger.debug(f"RAW-Response: {response.content!r}")
    response_data = json.loads(response.content)
    return model.model_validate(response_data.get("resource"))


async def listing(
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
    raise_when_operation_not_allowed(name, "list")
    if resource_id and issuer_id:
        raise ValueError("resource_id and issuer_id are mutually exclusive")

    model = lookup_model_by_name(name)  # early, also to test if name is registered

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

    if is_pageable:
        if next_page_token:
            params["token"] = next_page_token
        if result_per_page:
            params["maxResults"] = f"{result_per_page}"
        else:
            # default to 100, but this might need adjustment
            params["maxResults"] = "100"

    url = session_manager_async.url(name)

    async with session_manager_async.session(credentials=credentials) as session:
        while True:
            response = await session.get(url=url, params=params)
            # Use shared error handling for consistent exception types
            if name.endswith("Object"):
                resource_identifier = resource_id if resource_id else ""
            else:
                resource_identifier = issuer_id if issuer_id else ""
            handle_response_errors(response, "list", name, resource_identifier)

            data = json.loads(response.content)
            data = PaginatedResponse.model_validate(data)
            resources = data.resources
            pagination = data.pagination

            if not resources:
                logger.warning("Response does not contain 'resources'")
                if pagination and pagination.resultsPerPage == 0:
                    logger.warning(
                        "No results per page set, this might be an error in the API response."
                    )
                    break
            for count, record in enumerate(resources):
                try:
                    yield model.model_validate(record)
                except Exception:
                    logger.exception(f"Error validating record {count}:\n{record}")
                    raise
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
