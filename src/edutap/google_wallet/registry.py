from enum import StrEnum


class RegistrationType(StrEnum):
    WALLETCLASS = "walletClass"
    WALLETOBJECT = "walletObject"


_REGISTRY = {
    RegistrationType.WALLETCLASS: {},
    RegistrationType.WALLETOBJECT: {},
}


class register_model:
    def __init__(self, registration_type: RegistrationType, name: str) -> None:
        self.registration_type = registration_type
        self.name = name

    def __call__(self, cls: type) -> type:
        cls.__registration_type__ = self.registration_type
        cls.__registration_name__ = self.name
        if self.name in _REGISTRY[self.registration_type]:
            raise ValueError(
                f"Duplicate registration of {self.registration_type}: {self.name}"
            )
        _REGISTRY[self.registration_type][self.name] = cls
        return cls


def lookup(registration_type: RegistrationType, name: str) -> type:
    return _REGISTRY[registration_type][name]
