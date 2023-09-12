from pydantic import BaseModel

_MODEL_REGISTRY = {}


class register_model:
    def __init__(
        self,
        name: str,
        *,
        url_part: str | None = None,
        can_create: bool = True,
        can_read: bool = True,
        can_update: bool = True,
        can_disable: bool = True,
        can_message: bool = False,
    ):
        self.metadata = {
            "name": name,
            "url_part": url_part or name,
            "can_create": can_create,
            "can_read": can_read,
            "can_update": can_update,
            "can_disable": can_disable,
            "can_message": can_message,
        }

    def __call__(self, cls: BaseModel) -> BaseModel:
        name = self.metadata["name"]
        if name in _MODEL_REGISTRY:
            raise ValueError(f"Duplicate registration of '{name}'")
        self.metadata["model"] = cls
        _MODEL_REGISTRY[name] = self.metadata
        return cls


def lookup_model(name: str) -> BaseModel:
    return _MODEL_REGISTRY[name]["model"]


def lookup_metadata(name: str) -> dict[str:any]:
    return _MODEL_REGISTRY[name]


def raise_when_operation_not_allowed(name, operation):
    """Verifies that the given operation is allowed for the given registered name.

    :raises: ValueError when the operation is not allowed.
    """
    if not _MODEL_REGISTRY[name][f"can_{operation}"]:
        raise ValueError(f"Operation '{operation}' not allowed for '{name}'")
