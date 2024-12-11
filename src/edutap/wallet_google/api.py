from .models.bases import Model
from .models.datatypes.general import Pagination
from .models.datatypes.message import Message
from .models.misc import AddMessageRequest
from .models.misc import ObjectWithClassReference
from .registry import lookup_metadata
from .registry import lookup_model
from .registry import lookup_model_by_plural_name
from .registry import raise_when_operation_not_allowed
from .session import session_manager
from collections.abc import Generator
from google.auth import crypt
from google.auth import jwt

import json
import logging
import typing


logger = logging.getLogger(__name__)


def _validate_data(model: type[Model], data: dict[str, typing.Any] | Model) -> Model:
    """Takes a model and data, validates it and convert to a json string.

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


def _validate_data_and_convert_to_json(
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
    verified_data = _validate_data(model, data)
    verified_json = verified_data.model_dump_json(
        exclude_none=not existing,  # exclude None values when we create something new
        exclude_unset=True,  # exclude unset values - this are values not set explicitly by the code
        by_alias=True,
    )
    identifier = getattr(verified_data, resource_id_key)
    # nice to have: if existing: check if this is a valid identifier using read
    return (identifier, verified_json)


def create(
    name: str,
    data: dict[str, typing.Any] | Model,
) -> Model:
    """
    Creates a Google Wallet items. `C` in CRUD.

    :param name:       Registered name of the model to use
    :param data:       Data to pass to the Google RESTful API.
                       Either a simple python data structure using built-ins,
                       or a Pydantic model instance matching the registered name's model.
    :raises Exception: When the response status code is not 200.
    :return:           The created model based on the data returned by the Restful API.
    """
    raise_when_operation_not_allowed(name, "create")
    model = lookup_model(name)
    resource_id, verified_json = _validate_data_and_convert_to_json(model, data)
    session = session_manager.session
    url = session_manager.url(name)
    headers = {"Content-Type": "application/json"}
    response = session.post(
        url=url,
        data=verified_json.encode("utf-8"),
        headers=headers,
    )
    if response.status_code == 409:
        raise Exception(
            f"Wallet Object {name} {getattr(data, 'id', 'No ID')} already exists\n{response.text}"
        )
    elif response.status_code != 200:
        raise Exception(f"Error at {url}: {response.status_code} - {response.text}")

    logger.debug(f"RAW-Response: {response.content!r}")
    return model.model_validate_json(response.content)


def read(
    name: str,
    resource_id: str,
) -> Model:
    """
    Reads a Google Wallet Class or Object. `R` in CRUD.

    :param name:               Registered name of the model to use
    :param resource_id:        Identifier of the resource to read from the Google RESTful API
    :raises LookupError:       When the resource was not found (404).
    :raises Exception:         When the response status code is not 200 or 404.
    :return:                   the created model based on the data returned by the Restful API
    """
    raise_when_operation_not_allowed(name, "read")
    session = session_manager.session
    url = session_manager.url(name, f"/{resource_id}")
    response = session.get(url=url)

    if response.status_code == 404:
        raise LookupError(f"{url}: {name} not found")

    if response.status_code == 200:
        model = lookup_model(name)
        logger.debug(f"RAW-Response: {response.content!r}")
        return model.model_validate_json(response.content)

    raise Exception(f"{url} {response.status_code} - {response.text}")


def update(
    name: str,
    data: dict[str, typing.Any] | Model,
    *,
    partial: bool = True,
) -> Model:
    """
    Updates a Google Wallet Class or Object. `U` in CRUD.

    :param name:         Registered name of the model to use
    :param data:         Data to pass to the Google RESTful API.
                         Either a simple python data structure using built-ins,
                         or a Pydantic model instance matching the registered name's model.
    :param override_all: When True, all fields will be overwritten, otherwise only given fields.
    :raises LookupError: When the resource was not found (404)
    :raises Exception:   When the response status code is not 200 or 404
    :return:             The created model based on the data returned by the Restful API
    """
    raise_when_operation_not_allowed(name, "update")
    model_metadata = lookup_metadata(name)
    model = model_metadata["model"]
    if not isinstance(data, Model) and partial:
        resource_id = data[model_metadata["resource_id"]]
        # we can not validate partial data for patch yet
        verified_json = json.dumps(data)
    else:
        resource_id, verified_json = _validate_data_and_convert_to_json(
            model, data, existing=True, resource_id_key=model_metadata["resource_id"]
        )
    session = session_manager.session
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
    if response.status_code == 404:
        raise LookupError(
            f"Error 404, {name} {getattr(data, 'id', 'No ID')} not found: - {response.text}"
        )

    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code} - {response.text}")

    logger.debug(f"RAW-Response: {response.content!r}")
    return model.model_validate_json(response.content)


def message(
    name: str,
    resource_id: str,
    message: dict[str, typing.Any] | Message,
) -> Model:
    """Sends a message to a Google Wallet Class or Object.

    :param name:         Registered name of the model to use
    :param resource_id:  Identifier of the resource to send to
    :raises LookupError: When the resource was not found (404)
    :raises Exception:   When the response status code is not 200 or 404
    :return:             The created Model object as returned by the Restful API
    """
    raise_when_operation_not_allowed(name, "message")
    model_metadata = lookup_metadata(name)
    model = model_metadata["model"]
    if not isinstance(message, Message):
        message_validated = Message.model_validate(message)
    else:
        message_validated = message
    add_message = AddMessageRequest(message=message_validated)
    verified_json = add_message.model_dump_json(
        exclude_none=True,
    )
    session = session_manager.session
    url = session_manager.url(name, f"/{resource_id}/addMessage")
    response = session.post(url=url, data=verified_json.encode("utf-8"))

    if response.status_code == 404:
        raise LookupError(f"Error 404, {name} not found: - {response.text}")

    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code} - {response.text}")
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
) -> Generator[Model | str, None, None]:
    """Lists wallet related resources.

    It is possible to list all classes of an issuer. Parameter 'name' has to end with 'Class',
    all objects of a registered object type by it's classes resource id,
    Parameter 'name' has to end with 'Object'.
    To get all issuers, parameter 'name' has to be 'Issuer' and no further parameters are allowed.

    :param name:            Registered name to base the listing on.
    :param resource_id:     Id of the class to list objects of.
                            Only for object listings`
                            Mutually exclusive with issuer_id.
    :param issuer_id:       Identifier of the issuer to list classes of.
                            Only for class listings.
                            If no resource_id is given and issuer_id is None, it will
                            be fetched from the environment variable EDUTAP_WALLET_GOOGLE_ISSUER_ID.
                            Mutually exclusive with resource_id.
    :param result_per_page: Number of results per page to fetch.
                            If omitted all results will be fetched and provided by the generator.
    :param next_page_token: Token to get the next page of results.
    :raises ValueError:     When input was invalid.
    :raises LookupError:    When the resource was not found (404)
    :raises Exception:      When the response status code is not 200 or 404
    :return:                Generator of the data as model-instances based on the data returned by the
                            Restful API. When result_per_page is given, the generator will return
                            a next_page_token after the last model-instance result.
    """
    raise_when_operation_not_allowed(name, "list")
    if resource_id and issuer_id:
        raise ValueError("resource_id and issuer_id are mutually exclusive")

    model = lookup_model(name)  # early, also to test if name is registered

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
            issuer_id = session_manager.settings.issuer_id
            if not issuer_id:
                raise ValueError(
                    "'issuer_id' must be passed as keyword argument or set in environment"
                )
        params["issuerId"] = issuer_id

    if is_pageable:
        if next_page_token:
            params["token"] = next_page_token
        if result_per_page:
            params["maxResults"] = f"{result_per_page}"
        else:
            # default to 100, but this might need adjustment
            params["maxResults"] = "100"

    url = session_manager.url(name)
    session = session_manager.session
    while True:
        response = session.get(url=url, params=params)
        if response.status_code == 404:
            raise LookupError(f"Error 404, {name} not found: - {response.text}")

        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.text}")

        data = json.loads(response.content)
        for count, record in enumerate(data["resources"]):
            try:
                yield model.model_validate(record)
            except Exception:
                logger.error(f"Error validating record {count}:\n{record}")
                raise
        if not is_pageable:
            break
        pagination = Pagination.model_validate(data["pagination"])
        if result_per_page > 0:
            if pagination.nextPageToken:
                yield pagination.nextPageToken
                break
        else:
            if pagination.nextPageToken:
                params["token"] = pagination.nextPageToken
                continue
        break


def save_link(
    resources: dict[str, list[Model | dict]],
    *,
    origins: list[str] = [],
) -> str:
    """
    Creates a link to save a Google Wallet Object to the wallet on the device.

    Besides the capability to save an object to the wallet, it is also able create classes on-the-fly.

    :param resources:   Dictionary of resources to save.
                        Each dictionary key is the registered plural name of a model.
                        Usually, this is the name with a lower first character and as plural.
                        The value is either a simple python data structure using built-ins,
                        or a Pydantic model instance matching the registered name's model.
                        If a resource is an Object, it can be an ObjectReference instance too.
    :param origins:     List of domains to approve for JWT saving functionality.
                        The Google Wallet API button will not render when the origins field is not defined.
                        You could potentially get an "Load denied by X-Frame-Options" or "Refused to display"
                        messages in the browser console when the origins field is not defined.
    :return:            Link with JWT to save the resources to the wallet.
    """
    # validate resources
    payload: dict[str, typing.Any] = {}
    for name, objs in resources.items():
        payload[name] = []
        for obj in objs:

            # first look if this is a reference to an existing wallet object passed as dict
            if isinstance(obj, dict) and (
                ("id" in obj and len(obj.keys()) == 1)
                or ("id" in obj and "classReference" in obj and len(obj.keys()) == 2)
            ):
                obj = ObjectWithClassReference.model_validate(obj)

            # if it is not a reference, it must be a full wallet object model
            if not isinstance(obj, ObjectWithClassReference):
                model = lookup_model_by_plural_name(name)
                obj = _validate_data(model, obj)

            # dump the model to json
            obj_json = obj.model_dump(
                # explicitly set to model_dump(mode="json") instead of model_dump_json due to problems
                # reported by jensens
                mode="json",
                exclude_none=True,  # exclude None values - here we create something new, no updates.
                exclude_unset=True,  # exclude unset values - this are values not set explicitly by the code
                by_alias=True,
            )
            # append to the current payload section
            payload[name].append(obj_json)

    claims = {
        "iat": "",
        "iss": session_manager.settings.credentials_info["client_email"],
        "aud": "google",
        "origins": origins,
        "typ": "savetowallet",
        "payload": payload,
    }
    signer = crypt.RSASigner.from_service_account_file(
        session_manager.settings.credentials_file
    )
    jwt_string = jwt.encode(signer, claims).decode("utf-8")
    if len(jwt_string) >= 1800:
        logger.debug(
            "JWT-Length: %d, is larger than recommended 1800 bytes: %s",
            len(jwt_string),
            len(jwt_string) >= 1800,
        )
    return f"{session_manager.settings.save_url}/{jwt_string}"
