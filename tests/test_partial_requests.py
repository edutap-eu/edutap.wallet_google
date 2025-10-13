from edutap.wallet_google import api
from edutap.wallet_google.clientpool import client_pool
from edutap.wallet_google.models.bases import Model
from edutap.wallet_google.models.datatypes import enums
from typing import Any

import httpx
import pytest
import respx


@respx.mock
def test_get_partial_read(mock_session) -> None:
    fields = [
        "id",
        # "kind",
        "classId",
    ]

    obj_id = "3388000000022141777.obj53.test.ycc.edutap"
    class_id = "3388000000022141777.test.ycc.edutap"

    url = (
        client_pool.url("GenericObject")
        + "/"
        + obj_id
        + "?fields="
        + "%2C".join(fields)
    )
    print(url)
    # Mock the GET request
    respx.get(url).mock(
        return_value=httpx.Response(
            200,
            json={
                "id": obj_id,
                "classId": class_id,
            },
        )
    )

    obj: Model | dict[str, Any] = api.read(
        "GenericObject",
        resource_id=obj_id,
        fields=fields,
    )
    assert isinstance(obj, dict)
    print(obj)
    assert set(fields) == set(obj.keys())
    assert obj["id"] == obj_id
    assert obj["classId"] == class_id


@pytest.mark.asyncio
@respx.mock
async def test_get_partial_aread(mock_async_session) -> None:
    fields = [
        "id",
        # "kind",
        "classId",
    ]

    obj_id = "3388000000022141777.obj53.test.ycc.edutap"
    class_id = "3388000000022141777.test.ycc.edutap"

    url = (
        client_pool.url("GenericObject")
        + "/"
        + obj_id
        + "?fields="
        + "%2C".join(fields)
    )
    print(url)
    # Mock the GET request
    respx.get(url).mock(
        return_value=httpx.Response(
            200,
            json={
                "id": obj_id,
                "classId": class_id,
            },
        )
    )

    obj: Model | dict[str, Any] = await api.aread(
        "GenericObject",
        resource_id=obj_id,
        fields=fields,
    )
    assert isinstance(obj, dict)
    print(obj)
    assert set(fields) == set(obj.keys())
    assert obj["id"] == obj_id
    assert obj["classId"] == class_id


@respx.mock
def test_create_partial_sync(mock_session) -> None:
    name = "GenericObject"
    object_id = "partial.create.1"
    url = client_pool.url(name)

    fields = ["id", "state"]
    # Mock POST returning only a subset of fields
    respx.post(url, params={"fields": ",".join(fields)}).mock(
        return_value=httpx.Response(200, json={"id": object_id, "state": "ACTIVE"})
    )

    data = api.new(
        name, {"id": object_id, "classId": "cls.1", "state": enums.State.ACTIVE}
    )
    result = api.create(data, fields=fields)

    assert isinstance(result, dict)
    assert result["id"] == object_id
    assert result["state"] == "ACTIVE"


@pytest.mark.asyncio
@respx.mock
async def test_acreate_partial_async(mock_async_session) -> None:
    name = "GenericObject"
    object_id = "partial.create.2"
    url = client_pool.url(name)

    fields = ["id", "state"]
    respx.post(url, params={"fields": ",".join(fields)}).mock(
        return_value=httpx.Response(200, json={"id": object_id, "state": "INACTIVE"})
    )

    data = api.new(
        name, {"id": object_id, "classId": "cls.1", "state": enums.State.INACTIVE}
    )
    result = await api.acreate(data, fields=fields)

    assert isinstance(result, dict)
    assert result["id"] == object_id
    assert result["state"] == "INACTIVE"


@respx.mock
def test_update_partial_sync(mock_session) -> None:
    name = "GenericObject"
    object_id = "partial.update.1"
    url = client_pool.url(name, f"/{object_id}")

    fields = ["id", "state"]
    respx.patch(url, params={"fields": ",".join(fields)}).mock(
        return_value=httpx.Response(200, json={"id": object_id, "state": "EXPIRED"})
    )

    data = api.new(
        name, {"id": object_id, "classId": "cls.1", "state": enums.State.EXPIRED}
    )
    result = api.update(data, partial=True, fields=fields)

    assert isinstance(result, dict)
    assert result["id"] == object_id
    assert result["state"] == "EXPIRED"


@pytest.mark.asyncio
@respx.mock
async def test_aupdate_partial_async(mock_async_session) -> None:
    name = "GenericObject"
    object_id = "partial.update.2"
    url = client_pool.url(name, f"/{object_id}")

    fields = ["id", "state"]
    respx.patch(url, params={"fields": ",".join(fields)}).mock(
        return_value=httpx.Response(200, json={"id": object_id, "state": "INACTIVE"})
    )

    data = api.new(
        name, {"id": object_id, "classId": "cls.1", "state": enums.State.INACTIVE}
    )
    result = await api.aupdate(data, partial=True, fields=fields)

    assert isinstance(result, dict)
    assert result["id"] == object_id
    assert result["state"] == "INACTIVE"


@respx.mock
def test_message_partial_sync(mock_session) -> None:
    name = "GenericObject"
    object_id = "partial.msg.1"
    url = client_pool.url(name, f"/{object_id}/addMessage")

    fields = ["resource.id"]
    respx.post(url, params={"fields": ",".join(fields)}).mock(
        return_value=httpx.Response(
            200, json={"resource": {"id": object_id, "state": "ACTIVE"}}
        )
    )

    result = api.message(name, object_id, {"header": "h", "body": "b"}, fields=fields)

    assert isinstance(result, dict)
    assert "resource" in result
    assert result["resource"]["id"] == object_id


@pytest.mark.asyncio
@respx.mock
async def test_amessage_partial_async(mock_async_session) -> None:
    name = "GenericObject"
    object_id = "partial.msg.2"
    url = client_pool.url(name, f"/{object_id}/addMessage")

    fields = ["id", "messages"]
    respx.post(url, params={"fields": ",".join(fields)}).mock(
        return_value=httpx.Response(
            200, json={"resource": {"id": object_id, "state": "ACTIVE"}}
        )
    )

    result = await api.amessage(
        name, object_id, {"header": "h", "body": "b"}, fields=fields
    )

    assert isinstance(result, dict)
    assert "resource" in result
    assert result["resource"]["id"] == object_id


@respx.mock
def test_listing_partial_sync(mock_session) -> None:
    name = "GenericClass"
    issuer_id = "issuer.partial"
    url = client_pool.url(name)

    fields = ["id"]
    respx.get(url, params={"issuerId": issuer_id, "fields": ",".join(fields)}).mock(
        return_value=httpx.Response(
            200,
            json={
                "resources": [
                    {"id": f"{issuer_id}.class1"},
                    {"id": f"{issuer_id}.class2"},
                ]
            },
        )
    )

    results = []
    for item in api.listing(name, issuer_id=issuer_id, fields=fields):
        results.append(item)

    assert len(results) == 2
    assert isinstance(results[0], dict)
    assert results[0]["id"] == f"{issuer_id}.class1"


@pytest.mark.asyncio
@respx.mock
async def test_alisting_partial_async(mock_async_session) -> None:
    name = "GenericClass"
    issuer_id = "issuer.partial.async"
    url = client_pool.url(name)

    fields = ["id"]
    respx.get(url, params={"issuerId": issuer_id, "fields": ",".join(fields)}).mock(
        return_value=httpx.Response(
            200, json={"resources": [{"id": f"{issuer_id}.class1"}]}
        )
    )

    results = []
    async for item in api.alisting(name, issuer_id=issuer_id, fields=fields):
        results.append(item)

    assert len(results) == 1
    assert isinstance(results[0], dict)
    assert results[0]["id"] == f"{issuer_id}.class1"
