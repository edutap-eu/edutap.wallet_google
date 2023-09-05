from typing import Any


_REGISTRY = {}


class register:
    def __init__(self, name: str) -> None:
        self.name = name

    def __call__(self, cls: Any) -> Any:
        _REGISTRY[self.name] = cls
        return cls
