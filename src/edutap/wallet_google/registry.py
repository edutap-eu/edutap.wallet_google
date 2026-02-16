from .models.bases import Model
from pydantic import BaseModel
from pydantic._internal._model_construction import ModelMetaclass
from typing import TypedDict

import functools
import importlib
import inspect
import logging


logger = logging.getLogger(__name__)


class RegistryMetadataDict(TypedDict, total=False):
    """TypedDict for the metadata of a registered model."""

    model: "type[Model]"
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
_MODEL_REGISTRY_BY_MODEL: "dict[type[Model], RegistryMetadataDict]" = {}


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
        cls: "type[Model]",
    ) -> "type[Model]":
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


def lookup_model_by_name(name: str) -> "type[Model]":
    """
    Returns the model with the given name.
    """
    return _MODEL_REGISTRY_BY_NAME[name]["model"]


def lookup_model_by_plural_name(plural_name: str) -> "type[Model]":
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


def lookup_metadata_by_model_instance(model: "Model") -> RegistryMetadataDict:
    """
    Returns the registry metadata by a given instance of a model
    """
    return _MODEL_REGISTRY_BY_MODEL[type(model)]


def lookup_metadata_by_model_type(model_type: "type[Model]") -> RegistryMetadataDict:
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


@functools.cache
def _find_models() -> dict[str, ModelMetaclass]:
    models: dict[str, ModelMetaclass] = {}
    pkg = importlib.import_module("edutap.wallet_google")
    datatypes_module = pkg.models.datatypes
    deprecated_module = pkg.models.deprecated

    def _collect_classes(mod):
        for cls_name, cls in inspect.getmembers(mod, inspect.isclass):
            if issubclass(cls, BaseModel) and cls is not BaseModel:
                models[cls_name] = cls

    # deprecated models
    for cls_name, cls in inspect.getmembers(deprecated_module, inspect.isclass):
        if (
            cls.__module__.startswith("edutap.wallet_google.models.deprecated")
            and issubclass(cls, BaseModel)
            and cls is not BaseModel
        ):
            models[cls_name] = cls

    # datatypes/*
    for name, module in inspect.getmembers(datatypes_module, inspect.ismodule):
        if module.__name__.startswith("edutap.wallet_google.models.datatypes"):
            _collect_classes(module)

    return models


@functools.cache
def _find_enums() -> list[str]:
    """
    Returns a list of all enum class names.
    """
    pkg = importlib.import_module("edutap.wallet_google")
    enums_module = pkg.models.datatypes.enums
    enums: list[str] = []
    for enum_name, enum in inspect.getmembers(enums_module, inspect.isclass):
        enums.append(enum_name)
    return enums


def validate_fields_for_name(name: str, fields: list[str]) -> tuple[bool, list[str]]:
    """Verifies that the given fields are valid for the given registered name.

    :raises: ValueError when any of the fields is not valid.
    """
    non_valid_fields = []

    model = lookup_model_by_name(name)
    model_fields = _get_fields_for_model(model)
    for field in fields:
        if field == "*":
            continue
        elif "/" in field:
            if "*" in field:
                first_part = field.split("*")[0][:-1]

                if first_part not in model_fields:
                    non_valid_fields.append(field)
                    continue
            elif field not in model_fields:
                non_valid_fields.append(field)
        elif "(" in field and ")" in field:
            first_part = field.split("(")[0]
            if first_part[:-1] not in model_fields:
                non_valid_fields.append(field)
                continue
        elif field not in model.model_fields:
            non_valid_fields.append(field)

    if non_valid_fields:
        # raise ValueError(f"Fields {non_valid_fields} not valid for '{name}'")
        logger.debug(f"Fields {', '.join(non_valid_fields)} not valid for '{name}'")
        return (False, non_valid_fields)
    return (True, [])


@functools.cache
def _get_fields_for_model(model: Model) -> list[str]:
    """Returns the list of valid fields for the given registered name."""
    fields: set[str] = set()
    # print(f"Getting fields for model: {model}")
    if model is BaseModel:
        return []
    schema = model.model_json_schema(by_alias=True)
    if schema is not None:
        properties = schema.get("properties", {})
        # breakpoint()
        for name, definition in properties.items():
            sub_fields = _get_fields_for_(name, definition)
            fields.update(sub_fields)
    return list(fields)


@functools.cache
def _get_fields_for_name(name: str) -> list[str]:
    """Returns the list of valid fields for the given registered name."""
    if "__" in name:
        name = name.split("__")[-1]
    model: ModelMetaclass | None = None
    if name in _MODEL_REGISTRY_BY_NAME:
        model = lookup_model_by_name(name)
    if model is None:
        models: dict[str, ModelMetaclass] = _find_models()
        model = models.get(name)
    if model is None:
        if name in _find_enums():
            return [name]
        raise ValueError(f"Model '{name}' not found")
    return _get_fields_for_model(model)


# @functools.cache
def _get_fields_for_(name, definition: dict) -> list[str]:
    """Returns the list of valid fields for the given schema object."""
    fields: set[str] = set()
    if definition in ("string", "boolean"):
        fields.add(name)
    if definition.get("deprecated") is True:
        pass
    elif definition.get("type") in ("string", "boolean"):
        fields.add(name)
    elif definition.get("type") == "array":
        fields.add(name)
    elif definition.get("$ref") is not None:
        ref = definition["$ref"].replace("#/$defs/", "")
        fields.add(name)
        sub_fields = _get_fields_for_name(ref)
        for sub_field in sub_fields:
            fields.add(f"{name}/{sub_field}")
    elif definition.get("anyOf") is not None:
        for any_of in definition["anyOf"]:
            if any_of.get("type") == "null":
                fields.add(name)
            elif any_of.get("type") == "array":
                sub_fields = _get_fields_for_(name, any_of["items"])
                for sub_field in sub_fields:
                    fields.add(f"{name}/{sub_field}")
            elif any_of.get("type") in ("string", "boolean"):
                fields.add(name)
            elif any_of.get("$ref") is not None:
                ref = any_of["$ref"].replace("#/$defs/", "")
                fields.add(name)
                sub_fields = _get_fields_for_name(ref)
                for sub_field in sub_fields:
                    fields.add(f"{name}/{sub_field}")

            else:
                print(
                    f"Unhandled anyOf type: {any_of.get('type')} --> definition: {any_of}"
                )
                fields.add(name)
    elif definition.get("$ref") is not None:
        # nested object, we can add the field name, but not its sub-fields
        fields.add(name)
    elif definition.get("type") is None:
        fields.add(name)
    return list(fields)
