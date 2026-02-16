from edutap.wallet_google.registry import _MODEL_REGISTRY_BY_NAME
from edutap.wallet_google.registry import lookup_metadata_by_name
from httpx import get
from httpx import HTTPError
from pydantic._internal._model_construction import ModelMetaclass
from typing import Any
from typing import Dict
from typing import Set
from typing import Type

import importlib
import inspect
import json
import pathlib
import pytest


MODEL_ALIAS_DICT = {
    "AppLinkInfo": "AppLinkDataAppLinkInfo",
    "AppTarget": "AppLinkDataAppLinkInfoAppTarget",
    "Jwt": "JwtResource",
    "TotpDetails": "RotatingBarcodeTotpDetails",
    "TotpParameters": "RotatingBarcodeTotpDetailsTotpParameters",
}


def find_models() -> Dict[str, Type]:
    models: Dict[str, Type] = {}
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


def test_discovery_api(discovery_api_data: Dict[str, Any]):
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


def test_wallet_api(wallet_api_data: Dict[str, Any]):
    assert isinstance(wallet_api_data, dict)
    assert wallet_api_data["kind"] == "discovery#restDescription"
    assert wallet_api_data["discoveryVersion"] == "v1"
    assert wallet_api_data["version"] == "v1"
    # this is subject to change over time
    assert "revision" in wallet_api_data, "Expected 'revision' field in wallet_api_data API response"
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


def test_known_schemas(wallet_api_data: Dict[str, Any]):
    schemas: Dict[str, Dict[str, Any]] = wallet_api_data.get("schemas", {})
    assert isinstance(schemas, dict)
    assert len(schemas) > 0

    api_schemas: Set[str] = set()
    for elem in schemas.keys():
        if elem.endswith("Request") or elem.endswith("Response"):
            continue
        api_schemas.add(elem)

    our_schemas: Dict[str, Type] = {}
    our_known_schemas: Set[str] = set(_MODEL_REGISTRY_BY_NAME.keys())
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
        model_schema = model.model_json_schema().get("properties", {})

        assert (
            set(api_schema["properties"].keys()) == model_schema_names
        ), f"Set of properties does not match for: '{name}'"

        for prop, prop_schema in api_schema["properties"].items():
            assert prop in model_schema_names
            if "deprecated" in prop_schema:
                our_prop = model_schema[prop]
                assert (
                    our_prop.get("deprecated", False) is True
                ), f"The property: '{prop}' is deprecated, but not marked as such in our schema."


def test_methods(wallet_api_data: Dict[str, Any]):
    resources = wallet_api_data["resources"]

    model_names: Dict[str, str] = {m.lower(): m for m in _MODEL_REGISTRY_BY_NAME.keys()}
    print(f"Known Model names: {model_names}")

    for resource_name, resource in resources.items():
        print(f"\nChecking resource: '{resource_name}'", end=" ")
        if resource_name in ["walletobjects"]:
            print("--> NO Model with this name is registered.", end="")
            continue
        assert isinstance(resource, dict)
        assert "methods" in resource
        assert isinstance(
            resource["methods"], dict
        ), "--> does not have a 'methods' key or it is not a dictionary."

        if resource_name not in model_names:
            print("--> NO Model with this name is registered.", end="")
            continue
        model = lookup_metadata_by_name(
            model_names[resource_name]
        )  # Ensure the resource is registered

        print(f"--> check with model: '{model['name']}'", end="")
        assert model["name"].lower() == resource_name

        expected_methods: Set[str] = set()
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
