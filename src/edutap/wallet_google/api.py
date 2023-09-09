from . import registry
from .models.primitives import Pagination
from .models.primitives.notification import AddMessageRequest
from .models.primitives.notification import Message
from .session import session_manager
from google.auth.transport.requests import AuthorizedSession
from pydantic import BaseModel

import json


def _make_url(
    model: type,
    additional_path: str | None = None,
) -> str:
    """
    Helper function to create the URL for the CRUD operations.

    For more information read

    :param model:  type of the model
    :return:       the url of the google RESTful API endpoint to handle this model
    """
    url_name = registry.lookup_url_name(model)
    return f"{session_manager.base_url}/{url_name}{f'/{additional_path}' if additional_path else ''}"


def create(
    *,
    model_data: BaseModel = None,
    model: type = None,
    **payload,
) -> BaseModel:
    """
    Creates a Google Wallet Class or Object. `C` in CRUD.

    :param model:              registered model to use
    :param payload:            data to pass to the Google RESTful API
    :raises Exception:         if the response status code is not 200
    :return:                   the created model based on the data returned by the API
    """

    session = session_manager.session
    data: str
    if model is None and model_data and payload:
        breakpoint()
        model = model_data.__class__

    elif model is None and model_data:
        model = model_data.__class__
        data = model_data.model_dump_json()
    elif model and payload:
        obj: BaseModel = model(**payload)
        data = obj.model_dump_json(
            exclude_none=True,
        )
    url = _make_url(model)
    response = session.post(url=url, data=data)

    if response.status_code != 200:
        raise Exception(f"Error at {url}: {response.status_code} - {response.text}")

    return model.model_validate_json(response.content)


def read(
    model: type,
    resource_id: str,
) -> BaseModel:
    """
    Reads a Google Wallet Class or Object. `R` in CRUD.

    :param model:              registered model to use
    :param resource_id:        id of the resource to read from the Google RESTful API
    :raises NotImplementedError: if the REST-method is not provided by the model
    :raises LookupError:       if the resource was not found (404)
    :raises Exception:         if the response status code is not 200 or 404
    :return:                   the created model based on the data returned by the API
    """
    session = session_manager.session
    if not registry.check_capability(cls=model, capability=registry.Capability.get):
        raise NotImplementedError(
            f"{capability} not implementend or supported by {model.__name__}"
        )
    url = _make_url(model, resource_id)
    response = session.get(url=url)

    if response.status_code == 404:
        raise LookupError(f"{url} {model.__name__} not found")

    if response.status_code == 200:
        return model.model_validate_json(response.content)

    raise Exception(f"{url} {response.status_code} - {response.text}")


def update(
    *,
    model_data: BaseModel | None = None,
    model: type | None = None,
    **payload,
) -> BaseModel:
    """
    Updates a Google Wallet Class or Object. `U` in CRUD.

    :param payload:            data to pass to the Google RESTful API
    :raises LookupError:       if the resource was not found (404)
    :raises Exception:         if the response status code is not 200 or 404
    :return:                   the created model based on the data returned by the API
    """
    session = session_manager.session
    obj: BaseModel
    if model_data and model_data.__class__ in registry._MODEL_REGISTRY.keys() and registry.check_capability(cls=model_data.__class__, registry.Capability.update) and not payload:
        obj = model_data
        model = model_data.__class__
    elif model and model in registry._MODEL_REGISTRY.keys() and registry.check_capability(cls=model_data.__class__, registry.Capability.update) and model_data is None and payload:
        obj = model(**payload)
    else:
        breakpoint()

    data = obj.model_dump_json(
        exclude_none=True,
        exclude_unset=True,
    )
    response = session.put(
        url=_make_url(model, obj.id),
        data=data.encode("utf-8"),
    )
    if response.status_code == 404:
        raise LookupError(f"{model.__name__} with id: {obj.id} not found")

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
