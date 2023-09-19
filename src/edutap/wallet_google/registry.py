from .modelbase import GoogleWalletModel


_MODEL_REGISTRY: dict[str, dict[str:any]] = {}


class register_model:
    """
    Registers a Pydantic model based on GoogleWalletModel in a registry.
    To be used as a decorator.
    """

    def __init__(
        self,
        name: str,
        url_part: str = None,
        *,
        plural: str | None = None,
        resource_id: str = "id",
        can_create: bool = True,
        can_read: bool = True,
        can_update: bool = True,
        can_disable: bool = True,
        can_list: bool = True,
        can_message: bool = True,
    ):
        """
        Prepares the registration of a GoogleWalletModel or its subclasses.

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
        :param can_disable: Whether it is possible to use in the 'disable' API function.
                            Defaults to True.
        :param can_list:    Whether it is possible to use in the 'list' API function.
                            Defaults to True.
        :param can_message: Whether it is possible to use in the 'message' API function.
                            Defaults to True.
        """
        self.metadata = {
            "name": name,
            "url_part": url_part,
            "plural": plural or f"{url_part}s",
            "resource_id": resource_id,
            "can_create": can_create,
            "can_read": can_read,
            "can_update": can_update,
            "can_disable": can_disable,
            "can_list": can_list,
            "can_message": can_message,
        }

    def __call__(self, cls: GoogleWalletModel) -> GoogleWalletModel:
        """
        Registers the given class in the registry.
        """
        name = self.metadata["name"]
        if name in _MODEL_REGISTRY:
            raise ValueError(f"Duplicate registration of '{name}'")
        self.metadata["model"] = cls
        _MODEL_REGISTRY[name] = self.metadata
        return cls


def lookup_model(name: str) -> GoogleWalletModel:
    """
    Returns the model with the given name.
    """
    return _MODEL_REGISTRY[name]["model"]


def lookup_model_by_plural_name(plural_name: str) -> GoogleWalletModel:
    """
    Returns the model with the given plural name.
    """
    for model in _MODEL_REGISTRY.values():
        if model["plural"] == plural_name:
            return model["model"]
    raise LookupError(f"Model with plural name '{plural_name}' not found")


def lookup_metadata(name: str) -> dict[str:any]:
    """
    Returns the metadata of the model with the given name.
    """
    return _MODEL_REGISTRY[name]


def raise_when_operation_not_allowed(name, operation):
    """Verifies that the given operation is allowed for the given registered name.

    :raises: ValueError when the operation is not allowed.
    """
    if not _MODEL_REGISTRY[name][f"can_{operation}"]:
        raise ValueError(f"Operation '{operation}' not allowed for '{name}'")
