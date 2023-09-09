from enum import StrEnum


_MODEL_REGISTRY = {}


class Capability(StrEnum):
    insert = "insert"
    get = "get"
    update = "update"
    patch = "patch"
    list = "list"
    addmessage = "addmessage"


class register_model:
    def __init__(
        self,
        url_name: str,
        *,
        has_insert: bool = True,
        has_get: bool = True,
        has_list: bool = True,
        has_update: bool = True,
        has_patch: bool = True,
        has_addmessage: bool = False,
    ) -> None:
        self.url_name = url_name
        self.has_insert = has_insert
        self.has_get = has_get
        self.has_list = has_list
        self.has_update = has_update
        self.has_patch = has_patch
        self.has_addmessage = has_addmessage

    def __call__(self, cls: type) -> type:
        if cls in _MODEL_REGISTRY.keys():
            raise ValueError(f"Duplicate registration of {cls.__name__}")
        _MODEL_REGISTRY[cls] = {
            "url_name": self.url_name,
            "has_insert": self.has_insert,
            "has_get": self.has_get,
            "has_list": self.has_list,
            "has_update": self.has_update,
            "has_patch": self.has_patch,
            "has_addmessage": self.has_addmessage,
        }
        return cls


def lookup_model(cls: type) -> str:
    """
    lookup the registerd model.

    :param cls: Model to lookup url path elem for
    :raises LookupError:         if the model was not found in registry
    """
    if cls not in _MODEL_REGISTRY.keys():
        raise LookupError(f"Unkown model type: {cls.__name__}")
    return cls


def lookup_url_name(cls: type) -> str:
    """
    lookup the url path element for the registerd model.

    :param cls: Model to lookup url path elem for
    :raises LookupError:         if the model was not found in registry
    :return:    url path element for registered model
    """
    if cls not in _MODEL_REGISTRY.keys():
        raise LookupError(f"Unkown model type: {cls.__name__}")
    return _MODEL_REGISTRY[cls]["url_name"]


def check_capability(cls: type, capability: Capability) -> bool:
    """
    Check if a model has a certain capability.

    :param cls:                  Model to be checked
    :raises LookupError:         if the model was not found in registry
    :raises NotImplementedError: if the REST-method is not provided by the model
    :return:                     true if the requested model provides that REST-method
    """
    if cls not in _MODEL_REGISTRY.keys():
        raise LookupError(f"Unkown model type: {cls.__name__}")
    has_capability: bool = _MODEL_REGISTRY[cls].get(f"has_{capability}", False)
    # if not has_capability:
    #     raise NotImplementedError(f"{capability} not implementend or supported by {cls.__name__}")
    return has_capability
