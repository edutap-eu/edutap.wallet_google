from enum import Enum
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import create_model

import functools
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


@functools.cache
def make_partial_model(model: type[Model]) -> type[Model]:
    """Create a model variant where all required fields become Optional with None default.

    The result is a subclass of the original model, so isinstance() checks
    against the original type still pass. Cached per model class.
    """
    field_overrides = {}
    for name, field_info in model.model_fields.items():
        if field_info.is_required() and field_info.annotation is not None:
            field_overrides[name] = (field_info.annotation | None, None)
    if not field_overrides:
        return model
    return create_model(
        f"Partial{model.__name__}",
        __base__=model,
        **field_overrides,
    )


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

    Google also publishes deprecated legacy spellings that follow no rule at
    all - ``EAN13`` for ``EAN_13``, ``qrcode`` for ``QR_CODE``. Those cannot be
    derived and are spelled out after the canonical value:

    class FooExample(CamelCaseAliasEnum):
        FOO_BAR_BAZ = "FOO_BAR_BAZ", "foobarbaz"

    The canonical value stays the member's value; the extra spellings are only
    accepted as input.
    """

    def __new__(
        cls: type["CamelCaseAliasEnum"], value: str, *extra_aliases: str
    ) -> "CamelCaseAliasEnum":
        obj: CamelCaseAliasEnum = object.__new__(cls)
        # Set explicitly: with extra aliases given, Enum would otherwise make
        # the whole argument tuple the member's value.
        obj._value_ = value
        obj._name_ = f"{cls.__name__} snake case literal"

        # create a second object per alias
        # creating an alias only does not work out since
        # pydantic checks for the value in the enum and not only the name
        for alias, kind in [
            (_snake_to_camel(value), "camel case alias"),
            *[(alias, "legacy alias") for alias in extra_aliases],
        ]:
            if alias in cls._value2member_map_:
                continue
            alias_obj = object.__new__(cls)
            alias_obj._value_ = alias
            alias_obj._name_ = f"{cls.__name__} {kind}"
            cls._value2member_map_[alias] = alias_obj
            cls._member_map_[alias] = alias_obj
            cls._member_names_.append(alias)
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
