from enum import Enum
from pydantic import BaseModel
from pydantic import ConfigDict

import typing


class Model(BaseModel):
    """
    Base Model for all Google Wallet Models.

    Sets a model_config for all Google Wallet Models that enforce that all attributes must be explicitly modeled, and trying to set an unknown attribute would raise an Exception.
    This Follows the Zen of Python (PEP 20) --> Explicit is better than implicit.
    """

    model_config = ConfigDict(
        extra="forbid",
        # use_enum_values=True,
    )


class WithIdModel(Model):
    """
    Model for Google Wallet models with an identifier.
    """

    id: str


def _snake_to_camel(snake_str: str) -> str:
    parts = snake_str.lower().split("_")
    return "".join(
        [(x.capitalize() if count != 0 else x) for count, x in enumerate(parts)]
    )


class CamelCaseAliasEnum(Enum):
    """Add an value alias in camelcase to the enum,
    given the value in snake-case.

    example: a enum like

    class FooExample(CamelCaseAliasEnum):
        FOO_BAR_BAZ = "FOO_BAR_BAZ"

    can be looked up like this:

    FooExample("fooBarBaz")

    """

    def __new__(cls: type["CamelCaseAliasEnum"], value: str) -> "CamelCaseAliasEnum":
        obj: "CamelCaseAliasEnum" = object.__new__(cls)
        obj._name_ = f"{cls.__name__} snake case literal"
        camel = _snake_to_camel(value)

        # create a second object with the camelcase name
        # creating an alias only does not work out since
        # pydantic checks for the value in the enum and not only the name
        camel_obj = object.__new__(cls)
        camel_obj._value_ = camel
        camel_obj._name_ = f"{cls.__name__} camel case alias"
        cls._value2member_map_[camel] = camel_obj
        cls._member_map_[camel] = camel_obj
        cls._member_names_.append(camel)
        return obj

    def __eq__(self, other: typing.Any | Enum) -> bool:
        """Allow comparison with the camelcase value.
        Take into account that UPPER_CASE and camelCase are equal
        """
        if not isinstance(other, Enum):
            other = self.__class__(other)
        if self.value == other.value:
            return True
        # this is not 100% correct, but should be good enough
        v1 = self.value.lower().replace("_", "")
        v2 = other.value.lower().replace("_", "")
        return v1 == v2
