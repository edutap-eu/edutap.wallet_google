from .models.bases import Model
from typing import TypedDict


class RegistryMetadataDict(TypedDict, total=False):
    """TypedDict for the metadata of a registered model."""

    model: type[Model]
    name: str
    url_part: str
    plural: str
    resource_id: str
    can_create: bool
    can_read: bool
    can_update: bool
    can_list: bool
    can_message: bool


_MODEL_REGISTRY_BY_NAME: dict[str, RegistryMetadataDict] = {}
_MODEL_REGISTRY_BY_MODEL: dict[type[Model], RegistryMetadataDict] = {}


class register_model:
    """
    Registers a Pydantic model based on Model in a registry.
    To be used as a decorator.
    """

    def __init__(
        self,
        name: str,
        url_part: str,
        *,
        plural: str | None = None,
        resource_id: str = "id",
        can_create: bool = True,
        can_read: bool = True,
        can_update: bool = True,
        can_list: bool = True,
        can_message: bool = True,
    ):
        """
        Prepares the registration of a Model or its subclasses.

        :param name:        Name of the model. Usually the same as the class name.
        :param url_part:    Part of the URL to be used for the RESTful API endpoint.
        :param plural:      Lowercase plural of the name. Defaults to url_part + 's'.
        :param resource_id: key name to fetch resource_id from. Defaults to 'id'.
        :param can_create:  Whether it is possible to use in the 'create' API function.
                            Defaults to True.
        :param can_read:    Whether it is possible to use in the 'read' API function.
                            Defaults to True.
        :param can_update:  Whether it is possible to use in the 'update' API function.
                            Defaults to True.
        :param can_list:    Whether it is possible to use in the 'list' API function.
                            Defaults to True.
        :param can_message: Whether it is possible to use in the 'message' API function.
                            Defaults to True.
        """
        self.metadata: RegistryMetadataDict = {
            "name": name,
            "url_part": url_part,
            "plural": plural or f"{url_part}s",
            "resource_id": resource_id,
            "can_create": can_create,
            "can_read": can_read,
            "can_update": can_update,
            "can_list": can_list,
            "can_message": can_message,
        }

    def __call__(
        self,
        cls: type[Model],
    ) -> type[Model]:
        """
        Registers the given class in the registry.
        """
        name = self.metadata["name"]
        if name in _MODEL_REGISTRY_BY_NAME:
            raise ValueError(f"Duplicate registration of '{name}'")
        self.metadata["model"] = cls
        _MODEL_REGISTRY_BY_NAME[name] = self.metadata
        _MODEL_REGISTRY_BY_MODEL[cls] = self.metadata
        return cls


def lookup_model_by_name(name: str) -> type[Model]:
    """
    Returns the model with the given name.
    """
    return _MODEL_REGISTRY_BY_NAME[name]["model"]


def lookup_model_by_plural_name(plural_name: str) -> type[Model]:
    """
    Returns the model with the given plural name.
    """
    for model in _MODEL_REGISTRY_BY_NAME.values():
        if model["plural"] == plural_name:
            return model["model"]
    raise LookupError(f"Model with plural name '{plural_name}' not found")


def lookup_metadata_by_name(name: str) -> RegistryMetadataDict:
    """
    Returns the metadata of the model with the given name.
    """
    return _MODEL_REGISTRY_BY_NAME[name]


def lookup_metadata_by_model_instance(model: Model) -> RegistryMetadataDict:
    """
    Returns the registry metadata by a given instance of a model
    """
    return _MODEL_REGISTRY_BY_MODEL[type(model)]


def lookup_metadata_by_model_type(model_type: type[Model]) -> RegistryMetadataDict:
    """
    Returns the registry metadata by a given model type
    """
    return _MODEL_REGISTRY_BY_MODEL[model_type]


def raise_when_operation_not_allowed(name: str, operation: str) -> None:
    """Verifies that the given operation is allowed for the given registered name.

    :raises: ValueError when the operation is not allowed.
    """
    if not _MODEL_REGISTRY_BY_NAME[name][f"can_{operation}"]:  # type: ignore
        raise ValueError(f"Operation '{operation}' not allowed for '{name}'")
