from edutap.wallet_google.registry import _MODEL_REGISTRY_BY_NAME
from edutap.wallet_google.registry import lookup_metadata_by_name
from enum import Enum
from httpx import get
from httpx import HTTPError
from pydantic import BaseModel
from pydantic._internal._model_construction import ModelMetaclass
from typing import Any

import importlib
import inspect
import json
import pathlib
import pytest
import typing


MODEL_ALIAS_DICT = {
    "AppLinkInfo": "AppLinkDataAppLinkInfo",
    "AppTarget": "AppLinkDataAppLinkInfoAppTarget",
    "Jwt": "JwtResource",
    "TotpDetails": "RotatingBarcodeTotpDetails",
    "TotpParameters": "RotatingBarcodeTotpDetailsTotpParameters",
}

# Schemas of Google's internal media/upload machinery. They are part of every
# discovery document Google publishes, they are not part of the Wallet data
# model, and no Wallet endpoint we call ever returns them.
GOOGLE_INTERNAL_SCHEMAS = {
    "Blobstore2Info",
    "CompositeMedia",
    "ContentTypeInfo",
    "DownloadParameters",
    "Media",
    "MediaRequestInfo",
    "ObjectId",
}


def find_models() -> dict[str, type]:
    models: dict[str, type] = {}
    pkg = importlib.import_module("edutap.wallet_google")
    datatypes_module = pkg.models.datatypes
    for name, module in inspect.getmembers(datatypes_module, inspect.ismodule):
        # print(f"Module: 'name', '{module}'")
        for cls_name, cls in inspect.getmembers(module, inspect.isclass):
            if (
                cls.__module__.startswith("edutap.wallet_google.models.datatypes")
                and cls.__class__ == ModelMetaclass
            ):
                # print(f"Class: '{cls_name}', '{cls}'")
                models[cls_name] = cls
    return models


def find_all_models() -> dict[str, type[BaseModel]]:
    """All Pydantic models of the package, keyed by class name.

    Unlike :func:`find_models` this walks the whole ``models`` package, so
    models living outside ``models/datatypes/`` (``models/misc.py``,
    ``models/deprecated.py``, ``models/passes/``) are found as well.
    """
    package = importlib.import_module("edutap.wallet_google.models")
    root = pathlib.Path(package.__path__[0])

    # Walking the file tree rather than using pkgutil: 'datatypes' carries no
    # __init__.py, so pkgutil does not descend into it.
    modules = []
    for path in sorted(root.rglob("*.py")):
        parts = path.relative_to(root).with_suffix("").parts
        if parts[-1] == "__init__":
            parts = parts[:-1]
        modules.append(importlib.import_module(".".join((package.__name__, *parts))))

    models: dict[str, type[BaseModel]] = {}
    for module in modules:
        for cls_name, cls in inspect.getmembers(module, inspect.isclass):
            if not cls.__module__.startswith("edutap.wallet_google.models"):
                continue
            if not issubclass(cls, BaseModel):
                continue
            # models/deprecated.py duplicates Image, ImageUri, LocalizedString
            # and friends to break an import cycle. Those copies are reduced to
            # what the deprecated fields need, so the real ones win.
            if cls.__module__.endswith(".deprecated") and cls_name in models:
                continue
            models[cls_name] = cls
    return models


def enum_types_of(annotation: Any) -> set[type[Enum]]:
    """Every Enum class reachable from a Pydantic field annotation.

    Fields are declared as ``Foo | None``, ``list[Foo]`` and the like, so the
    annotation has to be unwrapped recursively.
    """
    found: set[type[Enum]] = set()
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        found.add(annotation)
    for argument in typing.get_args(annotation):
        found |= enum_types_of(argument)
    return found


def find_enum_fields() -> dict[tuple[str, str], type[Enum]]:
    """Map ``(API schema name, property name)`` to the Enum class we use there.

    Derived from the models themselves rather than from a hand written table,
    so it cannot drift away from the code it describes.
    """
    fields: dict[tuple[str, str], type[Enum]] = {}
    for name, model in find_all_models().items():
        schema_name = MODEL_ALIAS_DICT.get(name, name)
        for field_name, field in model.model_fields.items():
            enums = enum_types_of(field.annotation)
            if len(enums) != 1:
                # No enum at all, or an ambiguous union - nothing to compare.
                continue
            fields[(schema_name, field.alias or field_name)] = enums.pop()
    return fields


def canonical_values(enum_class: type[Enum]) -> set[str]:
    """The values declared in the enum's class body, without generated aliases.

    :class:`~edutap.wallet_google.models.bases.CamelCaseAliasEnum` registers its
    aliases as extra members, so plain iteration would also yield them. An alias
    member does not carry the name it is registered under - that is what tells
    the two apart.
    """
    return {
        member.value
        for name, member in enum_class._member_map_.items()
        if member.name == name
    }


def api_enum_of(property_schema: dict[str, Any]) -> tuple[list[str], list[bool]] | None:
    """The enum values of a discovery property and their deprecation flags.

    Returns ``None`` for properties without an enum. Array properties carry the
    enum on their ``items``. ``enumDeprecated`` is absent whenever no value is
    deprecated, so a missing flag list means "nothing is deprecated".
    """
    schema = property_schema
    if schema.get("type") == "array":
        schema = schema.get("items", {})
    values = schema.get("enum")
    if values is None:
        return None
    deprecated = schema.get("enumDeprecated", [False] * len(values))
    return values, deprecated


def request_api_data_write_to_file(url: str, file_path: pathlib.Path) -> bool:
    try:
        response = get(url)
        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch data from '{url}'."
                f"Status code: {response.status_code}"
                f"Response: {response}"
            )
        # Save the API data to a local file
        # This is useful for offline testing and to avoid hitting the API rate limits
        # in case the API is called multiple times during testing.
        # The data is saved in a  JSON file.
        data = json.loads(response.text)
        with file_path.open("w") as fd:
            json.dump(data, fd, indent=2, sort_keys=True)
    except HTTPError as e:
        print(e)
        return False
    return True


@pytest.fixture(scope="module")
def module_tmp_path(tmp_path_factory):
    return tmp_path_factory.mktemp("module_tmp")


@pytest.fixture(scope="module")
def discovery_api_data(module_tmp_path):
    filename = module_tmp_path / "discovery_api_data.json"
    if not filename.exists():
        request_api_data_write_to_file(
            "https://discovery.googleapis.com/discovery/v1/apis?name=walletobjects",
            filename,
        )
    with filename.open("r") as file:
        yield json.load(file)


@pytest.fixture(scope="module")
def wallet_api_data(module_tmp_path):
    """Loads the Google Wallet API data from the local file."""
    filename = module_tmp_path / "wallet_api_data.json"
    if not filename.exists():
        request_api_data_write_to_file(
            "https://walletobjects.googleapis.com/$discovery/rest?version=v1",
            filename,
        )
    with filename.open("r") as file:
        yield json.load(file)


def check_if_url_is_not_reachable(url: str) -> bool:
    try:
        result = get(url)
        print(f"Status Code: {result.status_code}")
        if result.status_code == 200:
            print(f"URL: {url} is reachable.")
            return False
    except HTTPError as e:
        print(e)
    return True


# @pytest.mark.skipif(
#     check_if_url_is_not_reachable("https://discovery.googleapis.com/discovery/v1/apis?name=walletobjects"),
#     reason="This test is expected to fail if the discovery API data is not available."
# )
def test_load_data(discovery_api_data, wallet_api_data):
    """Test to ensure that the discovery API data can be loaded correctly."""
    assert isinstance(discovery_api_data, dict)
    assert isinstance(wallet_api_data, dict)


def test_discovery_api(discovery_api_data: dict[str, Any]):
    assert discovery_api_data["kind"] == "discovery#directoryList"
    assert discovery_api_data["discoveryVersion"] == "v1"
    assert len(discovery_api_data["items"]) == 1
    api_description = discovery_api_data["items"][0]
    assert isinstance(api_description, dict)
    assert "kind" in api_description
    assert api_description["kind"] == "discovery#directoryItem"
    assert "version" in api_description
    assert api_description["version"] == "v1"
    assert "id" in api_description
    assert api_description["id"] == "walletobjects:v1"
    assert "name" in api_description
    assert api_description["name"] == "walletobjects"
    assert "title" in api_description
    assert api_description["title"] == "Google Wallet API"
    assert "preferred" in api_description
    assert api_description["preferred"] is True
    assert "discoveryRestUrl" in api_description


def test_wallet_api(wallet_api_data: dict[str, Any]):
    assert isinstance(wallet_api_data, dict)
    assert wallet_api_data["kind"] == "discovery#restDescription"
    assert wallet_api_data["discoveryVersion"] == "v1"
    assert wallet_api_data["version"] == "v1"
    # this is subject to change over time
    assert "revision" in wallet_api_data, (
        "Expected 'revision' field in wallet_api_data API response"
    )
    print(f"\n\nWallet API Revision: {wallet_api_data['revision']}\n\n")
    # assert wallet_api_data["revision"] == "20250808"
    assert wallet_api_data["protocol"] == "rest"
    assert wallet_api_data["id"] == "walletobjects:v1"
    assert wallet_api_data["title"] == "Google Wallet API"
    assert wallet_api_data["canonicalName"] == "Walletobjects"
    assert wallet_api_data["name"] == "walletobjects"
    assert "resources" in wallet_api_data
    assert isinstance(wallet_api_data["resources"], dict)
    assert "schemas" in wallet_api_data
    assert isinstance(wallet_api_data["schemas"], dict)
    assert "parameters" in wallet_api_data
    assert isinstance(wallet_api_data["parameters"], dict)


def test_known_schemas(wallet_api_data: dict[str, Any]):
    schemas: dict[str, dict[str, Any]] = wallet_api_data.get("schemas", {})
    assert isinstance(schemas, dict)
    assert len(schemas) > 0

    api_schemas: set[str] = set()
    for elem in schemas.keys():
        if elem.endswith("Request") or elem.endswith("Response"):
            continue
        api_schemas.add(elem)

    our_schemas: dict[str, type] = {}
    our_known_schemas: set[str] = set(_MODEL_REGISTRY_BY_NAME.keys())
    for name in our_known_schemas:
        our_schemas[name] = lookup_metadata_by_name(name)["model"]

    for name, model in find_models().items():
        our_known_schemas.add(name)
        our_schemas[name] = model

    for name in [
        "JWTClaims",
        "JWTPayload",
        "PaginatedResponse",
        "Reference",
    ]:
        del our_schemas[name]

    # assert api_schemas == our_known_schemas, (
    #     f"\nAPI schemas do not match our known schemas."
    #     f"\nAPI schemas: {api_schemas}, "
    #     f"\nOur known schemas: {our_known_schemas}"
    #     f"\nDifference: {api_schemas - our_known_schemas}"
    # )

    our_schemas = dict(sorted(our_schemas.items()))
    # print("Our known schemas:")
    # for name in our_schemas.keys():
    #     print(f" * {name}")

    for name, model in our_schemas.items():
        # print(f"\nCheck: '{name}'", end=" ")

        api_schema = schemas.get(name, {})
        if api_schema == {} and name in MODEL_ALIAS_DICT.keys():
            api_schema = schemas.get(MODEL_ALIAS_DICT[name], {})
        assert api_schema
        # print(api_schema)
        try:
            if name not in MODEL_ALIAS_DICT.keys():
                assert api_schema["id"] == name
            assert api_schema["type"] == "object"
            assert "properties" in api_schema
            assert isinstance(api_schema["properties"], dict)
        except KeyError as e:
            print(f"Model: '{name}' has no property: '{e}'")

        model_schema_names = set(model.model_json_schema().get("properties", {}).keys())

        assert set(api_schema["properties"].keys()) == model_schema_names, (
            f"Set of properties does not match for: '{name}'"
        )
        # Deprecations are checked in both directions by
        # test_deprecated_properties, types by test_property_types.


def test_methods(wallet_api_data: dict[str, Any]):
    resources = wallet_api_data["resources"]

    model_names: dict[str, str] = {m.lower(): m for m in _MODEL_REGISTRY_BY_NAME.keys()}
    print(f"Known Model names: {model_names}")

    for resource_name, resource in resources.items():
        print(f"\nChecking resource: '{resource_name}'", end=" ")
        if resource_name in ["walletobjects"]:
            print("--> NO Model with this name is registered.", end="")
            continue
        assert isinstance(resource, dict)
        assert "methods" in resource
        assert isinstance(resource["methods"], dict), (
            "--> does not have a 'methods' key or it is not a dictionary."
        )

        if resource_name not in model_names:
            print("--> NO Model with this name is registered.", end="")
            continue
        model = lookup_metadata_by_name(
            model_names[resource_name]
        )  # Ensure the resource is registered

        print(f"--> check with model: '{model['name']}'", end="")
        assert model["name"].lower() == resource_name

        expected_methods: set[str] = set()
        if model["can_read"]:
            expected_methods.add("get")
        if model["can_list"]:
            expected_methods.add("list")
        if model["can_create"]:
            expected_methods.add("insert")
        if model["can_update"]:
            expected_methods.update({"update", "patch"})
        if model["can_message"]:
            expected_methods.add("addmessage")
        if model["name"] == "Permissions":
            expected_methods = {"get", "update"}

        available_methods = set(resource["methods"].keys())
        if "modifylinkedofferobjects" in available_methods:
            available_methods.remove("modifylinkedofferobjects")

        assert available_methods == expected_methods, (
            f"\nModel '{model['name']}' methods do not match the API methods."
            f"\nAPI methods do not match our expected methods."
            f"\nAPI methods: {resource['methods'].keys()}, "
            f"\nExpected methods: {expected_methods}"
            f"\nDifference: {available_methods - expected_methods}"
        )


def test_enum_values(wallet_api_data: dict[str, Any]):
    """Compare our enum values against the enums inlined in the discovery document.

    The discovery document holds no standalone enum schemas; every enum is
    inlined into the property that uses it. Google lists deprecated legacy
    spellings next to the canonical values and marks them via
    ``enumDeprecated``.

    Three things have to hold:

    1. Our canonical values are exactly Google's canonical values.
    2. Every value Google may send - legacy spellings included - is accepted by
       our enum, so reading an API response never fails on an alias.
    3. Wherever the API declares an enum, we use an enum too.
    """
    schemas: dict[str, dict[str, Any]] = wallet_api_data["schemas"]
    our_enum_fields = find_enum_fields()

    problems: dict[str, dict[str, list[str]]] = {
        "Google knows canonical values we do not": {},
        "we know canonical values Google does not": {},
        "our enum rejects values the API may send": {},
        "the API declares an enum where we use a plain type": {},
    }

    for schema_name, schema in sorted(schemas.items()):
        if schema_name in GOOGLE_INTERNAL_SCHEMAS:
            continue
        for property_name, property_schema in sorted(
            schema.get("properties", {}).items()
        ):
            api_enum = api_enum_of(property_schema)
            if api_enum is None:
                continue
            values, deprecated = api_enum
            where = f"{schema_name}.{property_name}"

            our_enum = our_enum_fields.get((schema_name, property_name))
            if our_enum is None:
                problems["the API declares an enum where we use a plain type"][
                    where
                ] = sorted(values)
                continue

            where = f"{our_enum.__name__} ({where})"
            api_canonical = {
                value
                for value, is_deprecated in zip(values, deprecated)
                if not is_deprecated
            }
            our_canonical = canonical_values(our_enum)

            if api_canonical - our_canonical:
                problems["Google knows canonical values we do not"][where] = sorted(
                    api_canonical - our_canonical
                )
            if our_canonical - api_canonical:
                problems["we know canonical values Google does not"][where] = sorted(
                    our_canonical - api_canonical
                )
            rejected = [
                value for value in values if value not in our_enum._value2member_map_
            ]
            if rejected:
                problems["our enum rejects values the API may send"][where] = rejected

    report = "\n".join(
        f"\n{headline}:\n"
        + "\n".join(
            f"  {where}: {values}" for where, values in sorted(findings.items())
        )
        for headline, findings in problems.items()
        if findings
    )
    assert not report, f"\nOur enums and the Wallet API disagree:\n{report}"


def api_wire_shape(property_schema: dict[str, Any], api_schemas: dict[str, Any]) -> str:
    """The JSON shape a discovery property describes.

    Reduced to what actually travels over the wire, because that is what both
    sides have to agree on. Google encodes int64 as a JSON string, so a
    ``format`` never changes the shape.
    """
    if "$ref" in property_schema:
        target = property_schema["$ref"]
        if api_schemas.get(target, {}).get("type") == "object":
            return f"object:{target}"
        return f"unknown:{target}"
    if "enum" in property_schema:
        return "enum"
    kind = property_schema.get("type")
    if kind == "array":
        return (
            f"array of {api_wire_shape(property_schema.get('items', {}), api_schemas)}"
        )
    return str(kind)


def our_wire_shape(property_schema: dict[str, Any], definitions: dict[str, Any]) -> str:
    """The JSON shape one of our model properties describes.

    Pydantic writes ``Foo | None`` as an ``anyOf`` over the type and null, and
    refines strings via ``format`` (uri, email, date-time). Neither changes the
    shape, so both are collapsed away.
    """
    if "anyOf" in property_schema:
        shapes = {
            our_wire_shape(variant, definitions)
            for variant in property_schema["anyOf"]
            if variant.get("type") != "null"
        }
        return shapes.pop() if len(shapes) == 1 else f"anyOf{sorted(shapes)}"
    if "$ref" in property_schema:
        key = property_schema["$ref"].rsplit("/", 1)[-1]
        definition = definitions.get(key, {})
        if "enum" in definition:
            return "enum"
        # Pydantic qualifies a $defs key with its module path whenever a class
        # name occurs twice: "..._deprecated__Image" instead of "Image".
        name = key.rsplit("__", 1)[-1]
        return f"object:{MODEL_ALIAS_DICT.get(name, name)}"
    kind = property_schema.get("type")
    if kind == "array":
        return (
            f"array of {our_wire_shape(property_schema.get('items', {}), definitions)}"
        )
    return str(kind)


def test_property_types(wallet_api_data: dict[str, Any]):
    """Compare the JSON type of every property against the discovery document.

    ``test_known_schemas`` compares property *names*; a field Google moved from
    ``string`` to ``object`` would not show up there.

    Required fields cannot be compared: the discovery document carries no
    ``required`` key on any schema, so there is nothing on Google's side to
    check ours against.
    """
    api_schemas: dict[str, dict[str, Any]] = wallet_api_data["schemas"]
    our_models = {
        MODEL_ALIAS_DICT.get(name, name): model
        for name, model in find_all_models().items()
    }

    mismatches: dict[str, str] = {}
    for schema_name, api_schema in sorted(api_schemas.items()):
        if schema_name in GOOGLE_INTERNAL_SCHEMAS or schema_name not in our_models:
            continue
        our_schema = our_models[schema_name].model_json_schema()
        our_properties = our_schema.get("properties", {})
        definitions = our_schema.get("$defs", {})

        for name, api_property in sorted(api_schema.get("properties", {}).items()):
            if name not in our_properties:
                continue  # covered by test_known_schemas
            expected = api_wire_shape(api_property, api_schemas)
            actual = our_wire_shape(our_properties[name], definitions)
            if expected != actual:
                mismatches[f"{schema_name}.{name}"] = (
                    f"API says {expected}, we say {actual}"
                )

    report = "\n".join(
        f"  {where}: {what}" for where, what in sorted(mismatches.items())
    )
    assert not report, f"\nProperty types disagree with the Wallet API:\n{report}"


# Properties we mark as deprecated although the discovery document does not.
# Google flags "locations" on every class but not on OfferObject; the wording of
# the description is identical, so this is an oversight on their side rather
# than a statement about the object.
DEPRECATED_BEYOND_THE_API = {
    "OfferObject.locations",
}


def api_says_deprecated(property_schema: dict[str, Any]) -> bool:
    """Whether the discovery document declares a property deprecated.

    The ``deprecated`` flag alone is not enough: Google sets it on
    ``EventTicketClass.infoModuleData`` but not on
    ``EventTicketObject.infoModuleData``, even though both descriptions read
    "Deprecated. Use textModulesData instead."
    """
    return bool(property_schema.get("deprecated")) or property_schema.get(
        "description", ""
    ).startswith("Deprecated")


def test_deprecated_properties(wallet_api_data: dict[str, Any]):
    """Every deprecation has to be visible on both sides.

    ``test_known_schemas`` only checks one direction - the API deprecates it, so
    we have to mark it. A field we still flag after Google has revived it is
    just as wrong, because our users see a warning that no longer applies.
    """
    api_schemas: dict[str, dict[str, Any]] = wallet_api_data["schemas"]
    our_models = {
        MODEL_ALIAS_DICT.get(name, name): model
        for name, model in find_all_models().items()
    }

    not_marked: list[str] = []
    marked_without_reason: list[str] = []
    for schema_name, api_schema in sorted(api_schemas.items()):
        if schema_name in GOOGLE_INTERNAL_SCHEMAS or schema_name not in our_models:
            continue
        our_properties = (
            our_models[schema_name].model_json_schema().get("properties", {})
        )

        for name, api_property in sorted(api_schema.get("properties", {}).items()):
            if name not in our_properties:
                continue  # covered by test_known_schemas
            where = f"{schema_name}.{name}"
            if where in DEPRECATED_BEYOND_THE_API:
                continue
            ours_says = bool(our_properties[name].get("deprecated"))
            if api_says_deprecated(api_property) and not ours_says:
                not_marked.append(where)
            if ours_says and not api_says_deprecated(api_property):
                marked_without_reason.append(where)

    assert not not_marked, (
        f"\nThe API deprecates these, we do not mark them: {not_marked}"
    )
    assert not marked_without_reason, (
        f"\nWe mark these deprecated, the API does not: {marked_without_reason}"
        f"\nEither drop the marker or add it to DEPRECATED_BEYOND_THE_API."
    )
