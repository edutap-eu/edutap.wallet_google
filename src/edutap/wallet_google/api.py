from .models.primitives import Pagination
from .models.primitives.notification import AddMessageRequest
from .models.primitives.notification import Message
from .registry import lookup
from .registry import RegistrationType
from .session import session_manager
from google.auth.transport.requests import AuthorizedSession
from pydantic import BaseModel


def _make_url(
    registration_type: RegistrationType,
    name: str,
    additional_path: str | None = None,
) -> str:
    """
    Helper function to create the URL for the CRUD operations.

    For more information read

    :param http_session: A Google authenticated session,
                         see https://googleapis.dev/python/google-auth/1.7.0/reference/google.auth.transport.requests.html#google.auth.transport.requests.AuthorizedSession

    :param registration_type:  type of the model (either class or object)
    :param name:               registered name of the model

    :return: the url of the google RESTful API endpoint to handle this model
    """
    base_type = (
        "Class" if registration_type == RegistrationType.WALLETCLASS else "Object"
    )
    return f"{session_manager.base_url}/{name}{base_type}{additional_path or ''}"


def create(
    registration_type: RegistrationType,
    name: str,
    **payload,
) -> BaseModel:
    """
    Creates a Google Wallet Class or Object. `C` in CRUD.

    :param registration_type:  type of the model (either class or object) to use
    :param name:               registered name of the model to use
    :param payload:            data to pass to the Google RESTful API
    :raises Exception:         if the response status code is not 200
    :return:                   the created model based on the data returned by the API
    """
    model = lookup(registration_type, name)
    obj = model(**payload)
    data = obj.json(
        exclude_none=True,
        exclude_unset=True,
    )
    session = session_manager.session
    url = _make_url(registration_type, name)
    response = session.post(url=url, data=data)

    if response.status_code != 200:
        raise Exception(f"Error at {url}: {response.status_code} - {response.text}")

    return model.parse_raw(response.content)


def read(
    registration_type: RegistrationType,
    name: str,
    resource_id: str,
) -> BaseModel:
    """
    Reads a Google Wallet Class or Object. `R` in CRUD.

    :param registration_type:  type of the model (either class or object) to use
    :param name:               registered name of the model to use
    :param resource_id:        id of the resource to read from the Google RESTful API
    :raises LookupError:       if the resource was not found (404)
    :raises Exception:         if the response status code is not 200 or 404
    :return:                   the created model based on the data returned by the API
    """
    session = session_manager.session
    response = session.get(
        url=_make_url(registration_type, name, f"/{resource_id}")
    )

    if response.status_code == 404:
        raise LookupError(f"{registration_type}: {name} not found")

    if response.status_code == 200:
        model = lookup(registration_type, name)
        return model.parse_raw(response.content)

    raise Exception(f"Error: {response.status_code} - {response.text}")


def update(
    registration_type: RegistrationType,
    name: str,
    **payload,
) -> BaseModel:
    """
    Updates a Google Wallet Class or Object. `U` in CRUD.

    :param registration_type:  type of the model (either class or object) to use
    :param name:               registered name of the model to use
    :param payload:            data to pass to the Google RESTful API
    :raises LookupError:       if the resource was not found (404)
    :raises Exception:         if the response status code is not 200 or 404
    :return:                   the created model based on the data returned by the API
    """
    model = lookup(registration_type, name)
    obj = model(**payload)
    data = obj.json(
        exclude_none=True,
        exclude_unset=True,
    )
    session = session_manager.session
    response = session.put(
        url=_make_url(registration_type, name, f"/{obj.id}"),
        data=data,
    )
    if response.status_code == 404:
        raise LookupError(f"{registration_type}: {name} not found")

    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code} - {response.text}")

    return model.parse_raw(response.content)


# def disable(
#     http_client: AuthorizedSession,
#     resource_id: str,
#     *,
#     obj_class: BaseModel,
# ):
#     """
#     Generic Implementation of the CRUD --> (D) usually delete, but here disbale since delete is not supported at Google Wallets.
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
#     Generic Implementation of the List Methode.
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
#     Generic Implementation addMessage Methode.
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
