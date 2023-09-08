from enum import StrEnum


class RegistrationType(StrEnum):
    WALLETCLASS = "walletClass"
    WALLETOBJECT = "walletObject"


_REGISTRY = {
    RegistrationType.WALLETCLASS: {},
    RegistrationType.WALLETOBJECT: {},
}

_MODEL_REGISTRY = {}


# class register_model:
#     def __init__(self, registration_type: RegistrationType, name: str) -> None:
#         self.registration_type = registration_type
#         self.name = name

#     def __call__(self, cls: type) -> type:
#         cls.__registration_type__ = self.registration_type
#         cls.__registration_name__ = self.name
#         if self.name in _REGISTRY[self.registration_type]:
#             raise ValueError(
#                 f"Duplicate registration of {self.registration_type}: {self.name}"
#             )
#         _REGISTRY[self.registration_type][self.name] = cls
#         return cls


def lookup(registration_type: RegistrationType, name: str) -> type:
    return _REGISTRY[registration_type][name]


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


def lookup_url_name(cls: type) -> str:
    return _MODEL_REGISTRY[cls]["url_name"]
