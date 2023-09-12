# from .models.primitives import Pagination
# from .models.primitives.notification import AddMessageRequest
# from .models.primitives.notification import Message
from .registry import lookup_model
from .registry import raise_when_operation_not_allowed
from .session import session_manager
from pydantic import BaseModel

import json


def _validate_data_and_convert_to_json(
    model, data: dict | BaseModel, *, fetch_id=False
) -> str | tuple[str, str]:
    """Takes a model and data, validates it and convert to a json string.

    :param model:      Pydantic model class to use for validation.
    :param data:       Data to pass to the Google RESTful API.
                       Either a simple python data structure using built-ins,
                       or a Pydantic model instance.
    :return:           JSON string of the data,
                       or, when fetch_id is True a tuple of resource-id and JSON string.
    """
    if not isinstance(data, BaseModel):
        verified_data = model.model_validate(data)
    else:
        if not isinstance(data, model):
            raise ValueError(
                f"Model of given data mismatches given name. Expected {model}, got {type(data)}."
            )
        verified_data = data
    verified_json = verified_data.model_dump_json(
        exclude_none=True,
    )
    if fetch_id:
        return (
            verified_data.id,
            verified_json,
        )
    return verified_json


def create(
    name: str,
    data: dict | BaseModel,
) -> BaseModel:
    """
    Creates a Google Wallet Class or Object. `C` in CRUD.

    :param name:       Registered name of the model to use
    :param data:       Data to pass to the Google RESTful API.
                       Either a simple python data structure using built-ins,
                       or a Pydantic model instance matching the registered name's model.
    :raises Exception: When the response status code is not 200.
    :return:           The created model based on the data returned by the API.
    """
    raise_when_operation_not_allowed(name, "create")
    model = lookup_model(name)
    verified_json = _validate_data_and_convert_to_json(model, data)
    session = session_manager.session
    url = session_manager.url(name)
    response = session.post(url=url, data=verified_json)

    if response.status_code != 200:
        raise Exception(f"Error at {url}: {response.status_code} - {response.text}")

    return model.model_validate_json(response.content)


def read(
    name: str,
    resource_id: str,
) -> BaseModel:
    """
    Reads a Google Wallet Class or Object. `R` in CRUD.

    :param name:               registered name of the model to use
    :param resource_id:        id of the resource to read from the Google RESTful API
    :raises LookupError:       if the resource was not found (404)
    :raises Exception:         if the response status code is not 200 or 404
    :return:                   the created model based on the data returned by the API
    """
    raise_when_operation_not_allowed(name, "read")
    session = session_manager.session
    url = session_manager.url(name, f"/{resource_id}")
    response = session.get(url=url)

    if response.status_code == 404:
        raise LookupError(f"{url}: {name} not found")

    if response.status_code == 200:
        model = lookup_model(name)
        return model.model_validate_json(response.content)

    raise Exception(f"{url} {response.status_code} - {response.text}")


def update(
    name: str,
    data: dict | BaseModel,
    *,
    override_all=False,
) -> BaseModel:
    """
    Updates a Google Wallet Class or Object. `U` in CRUD.

    :param name:       Registered name of the model to use
    :param data:       Data to pass to the Google RESTful API.
                       Either a simple python data structure using built-ins,
                       or a Pydantic model instance matching the registered name's model.
    :param override_all:       If True, all fields will be overwritten, otherwise only given fields.
    :raises LookupError:       if the resource was not found (404)
    :raises Exception:         if the response status code is not 200 or 404
    :return:                   the created model based on the data returned by the API
    """
    raise_when_operation_not_allowed(name, "update")
    model = lookup_model(name)
    if not isinstance(data, BaseModel) and not override_all:
        resource_id = data["id"]
        # we can not validate partial data for patch yet
        verified_json = json.dumps(data)
    else:
        resource_id, verified_json = _validate_data_and_convert_to_json(
            model, data, fetch_id=True
        )
    session = session_manager.session
    if override_all:
        response = session.put(
            url=session_manager.url(name, f"/{resource_id}"),
            data=verified_json,
        )
    else:
        response = session.patch(
            url=session_manager.url(name, f"/{resource_id}"),
            data=verified_json,
        )
    if response.status_code == 404:
        raise LookupError(f"Error 404, {name} not found: - {response.text}")

    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code} - {response.text}")

    return model.model_validate_json(response.content)


# def disable(
# registration_type: RegistrationType,
# name: str,
# resource_id: str,
# ):
#     """
#     Disables a Google Wallet Class or Object. `D` in CRUD.
#     Generic Implementation of the CRUD --> (D) usually delete, but here disable since delete is not supported at Google Wallets.
#     """
#     raise NotImplementedError()


# def list(
#     http_client: AuthorizedSession,
#     resource_id: str,
#     *,
#     obj_class: BaseModel,
#     max_results: int = 0,
#     token: str = None,
# ) -> list[BaseModel]:
#     """
#     Generic Implementation of the List Method.
#     """
#     response = None
#     url = f"{http_client.base_url}/{obj_class._url_path()}"
#     params = {}
#     if obj_class.__name__.endswith("Class"):
#         params["issuerId"] = resource_id
#     elif obj_class.__name__.endswith("Object"):
#         params["classId"] = resource_id

#     if max_results is not None and max_results > 0:
#         params["maxResults"] = max_results
#     if token is not None:
#         params["token"] = token
#     response = http_client.get(
#         url=url,
#         params=params,
#     )
#     objs = []
#     if response.status_code == 200:
#         data = json.loads(response.content)
#         pagination = Pagination.parse_obj(data["pagination"])
#         if pagination.resultsPerPage > 0:
#             raw_objs = data["resources"]
#             for elem in raw_objs:
#                 try:
#                     obj = obj_class.parse_obj(elem)
#                     objs.append(obj)
#                 except Exception as e:
#                     # breakpoint()
#                     print(e)
#     elif response.status_code == 404:
#         raise LookupError(f"No {obj_class.__name__} found")
#     else:
#         raise Exception(f"Error: {response.status_code} - {response.content}")
#     return objs


# def message(
#     http_client: AuthorizedSession,
#     resource_id: str,
#     message: Message,
#     *,
#     obj_class: BaseModel,
# ) -> BaseModel:
#     """
#     Generic Implementation addMessage Method.
#     """
#     response = http_client.post(
#         url=f"{http_client.base_url}/{obj_class._url_path()}/{resource_id}/addMessage",
#         data=AddMessageRequest(message=message).json(exclude_none=True),
#     )
#     if response.status_code == 200:
#         data = json.loads(response.content)
#         raw_obj = data["resource"]
#         return obj_class.parse_obj(raw_obj)
#     elif response.status_code == 404:
#         raise ValueError(f"{obj_class} {resource_id} does not exist.")
#     else:
#         raise Exception(f"Error: {response.status_code} - {response.content}")
