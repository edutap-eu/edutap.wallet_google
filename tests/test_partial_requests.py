"""Tests for partial response requests using the fields parameter.

These tests verify that when the `fields` parameter is used, API functions
return proper Model instances (with missing required fields set to None)
rather than raw dicts.
"""

import httpx
import pytest
import respx

from edutap.wallet_google import api
from edutap.wallet_google.clientpool import client_pool
from edutap.wallet_google.models.datatypes import enums
from edutap.wallet_google.models.passes import GenericClass, GenericObject

# --- Sync tests ---


@respx.mock
def test_read_partial_sync(mock_session) -> None:
    """Test that read() with fields returns a partial Model instance."""
    fields = ["id", "classId"]

    obj_id = "3388000000022141777.obj53.test.ycc.edutap"
    class_id = "3388000000022141777.test.ycc.edutap"

    url = client_pool.url("GenericObject", f"/{obj_id}")
    respx.get(url).mock(
        return_value=httpx.Response(
            200,
            json={
                "id": obj_id,
                "classId": class_id,
            },
        )
    )

    obj = api.read("GenericObject", resource_id=obj_id, fields=fields)

    assert isinstance(obj, GenericObject)
    assert obj.id == obj_id
    assert obj.classId == class_id
    assert "id" in obj.model_fields_set
    assert "classId" in obj.model_fields_set
    # state was not requested
    assert "state" not in obj.model_fields_set


@respx.mock
def test_create_partial_sync(mock_session) -> None:
    """Test that create() with fields returns a partial Model instance."""
    name = "GenericObject"
    object_id = "partial.create.1"
    url = client_pool.url(name)

    fields = ["id", "state"]
    respx.post(url).mock(
        return_value=httpx.Response(200, json={"id": object_id, "state": "ACTIVE"})
    )

    data = api.new(
        name, {"id": object_id, "classId": "cls.1", "state": enums.State.ACTIVE}
    )
    result = api.create(data, fields=fields)

    assert isinstance(result, GenericObject)
    assert result.id == object_id
    assert result.state == enums.State.ACTIVE
    assert "id" in result.model_fields_set
    assert "state" in result.model_fields_set
    assert result.classId is None
    assert "classId" not in result.model_fields_set


@respx.mock
def test_update_partial_sync(mock_session) -> None:
    """Test that update() with fields returns a partial Model instance."""
    name = "GenericObject"
    object_id = "partial.update.1"
    url = client_pool.url(name, f"/{object_id}")

    fields = ["id", "state"]
    respx.patch(url).mock(
        return_value=httpx.Response(200, json={"id": object_id, "state": "EXPIRED"})
    )

    data = api.new(
        name, {"id": object_id, "classId": "cls.1", "state": enums.State.EXPIRED}
    )
    result = api.update(data, partial=True, fields=fields)

    assert isinstance(result, GenericObject)
    assert result.id == object_id
    assert result.state == enums.State.EXPIRED
    assert "id" in result.model_fields_set
    assert "state" in result.model_fields_set
    assert result.classId is None
    assert "classId" not in result.model_fields_set


@respx.mock
def test_message_partial_sync(mock_session) -> None:
    """Test that message() with fields returns a partial Model instance."""
    name = "GenericObject"
    object_id = "partial.msg.1"
    url = client_pool.url(name, f"/{object_id}/addMessage")

    fields = ["resource.id"]
    respx.post(url).mock(
        return_value=httpx.Response(
            200, json={"resource": {"id": object_id, "state": "ACTIVE"}}
        )
    )

    result = api.message(name, object_id, {"header": "h", "body": "b"}, fields=fields)

    assert isinstance(result, GenericObject)
    assert result.id == object_id
    assert "id" in result.model_fields_set


@respx.mock
def test_listing_partial_sync(mock_session) -> None:
    """Test that listing() with fields yields partial Model instances."""
    name = "GenericClass"
    issuer_id = "issuer.partial"
    url = client_pool.url(name)

    fields = ["id"]
    respx.get(url).mock(
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

    results = list(api.listing(name, issuer_id=issuer_id, fields=fields))

    assert len(results) == 2
    assert all(isinstance(r, GenericClass) for r in results)
    assert results[0].id == f"{issuer_id}.class1"
    assert results[1].id == f"{issuer_id}.class2"


# --- Async tests ---


@pytest.mark.asyncio
@respx.mock
async def test_read_partial_async(mock_async_session) -> None:
    """Test that aread() with fields returns a partial Model instance."""
    fields = ["id", "classId"]

    obj_id = "3388000000022141777.obj53.test.ycc.edutap"
    class_id = "3388000000022141777.test.ycc.edutap"

    url = client_pool.url("GenericObject", f"/{obj_id}")
    respx.get(url).mock(
        return_value=httpx.Response(
            200,
            json={
                "id": obj_id,
                "classId": class_id,
            },
        )
    )

    obj = await api.aread("GenericObject", resource_id=obj_id, fields=fields)

    assert isinstance(obj, GenericObject)
    assert obj.id == obj_id
    assert obj.classId == class_id
    assert "id" in obj.model_fields_set
    assert "classId" in obj.model_fields_set
    assert "state" not in obj.model_fields_set


@pytest.mark.asyncio
@respx.mock
async def test_create_partial_async(mock_async_session) -> None:
    """Test that acreate() with fields returns a partial Model instance."""
    name = "GenericObject"
    object_id = "partial.create.2"
    url = client_pool.url(name)

    fields = ["id", "state"]
    respx.post(url).mock(
        return_value=httpx.Response(200, json={"id": object_id, "state": "INACTIVE"})
    )

    data = api.new(
        name, {"id": object_id, "classId": "cls.1", "state": enums.State.INACTIVE}
    )
    result = await api.acreate(data, fields=fields)

    assert isinstance(result, GenericObject)
    assert result.id == object_id
    assert result.state == enums.State.INACTIVE
    assert "id" in result.model_fields_set
    assert "state" in result.model_fields_set
    assert result.classId is None
    assert "classId" not in result.model_fields_set


@pytest.mark.asyncio
@respx.mock
async def test_update_partial_async(mock_async_session) -> None:
    """Test that aupdate() with fields returns a partial Model instance."""
    name = "GenericObject"
    object_id = "partial.update.2"
    url = client_pool.url(name, f"/{object_id}")

    fields = ["id", "state"]
    respx.patch(url).mock(
        return_value=httpx.Response(200, json={"id": object_id, "state": "INACTIVE"})
    )

    data = api.new(
        name, {"id": object_id, "classId": "cls.1", "state": enums.State.INACTIVE}
    )
    result = await api.aupdate(data, partial=True, fields=fields)

    assert isinstance(result, GenericObject)
    assert result.id == object_id
    assert result.state == enums.State.INACTIVE
    assert "id" in result.model_fields_set
    assert "state" in result.model_fields_set
    assert result.classId is None
    assert "classId" not in result.model_fields_set


@pytest.mark.asyncio
@respx.mock
async def test_message_partial_async(mock_async_session) -> None:
    """Test that amessage() with fields returns a partial Model instance."""
    name = "GenericObject"
    object_id = "partial.msg.2"
    url = client_pool.url(name, f"/{object_id}/addMessage")

    fields = ["id", "messages"]
    respx.post(url).mock(
        return_value=httpx.Response(
            200, json={"resource": {"id": object_id, "state": "ACTIVE"}}
        )
    )

    result = await api.amessage(
        name, object_id, {"header": "h", "body": "b"}, fields=fields
    )

    assert isinstance(result, GenericObject)
    assert result.id == object_id
    assert "id" in result.model_fields_set


@pytest.mark.asyncio
@respx.mock
async def test_listing_partial_async(mock_async_session) -> None:
    """Test that alisting() with fields yields partial Model instances."""
    name = "GenericClass"
    issuer_id = "issuer.partial.async"
    url = client_pool.url(name)

    fields = ["id"]
    respx.get(url).mock(
        return_value=httpx.Response(
            200, json={"resources": [{"id": f"{issuer_id}.class1"}]}
        )
    )

    results = []
    async for item in api.alisting(name, issuer_id=issuer_id, fields=fields):
        results.append(item)

    assert len(results) == 1
    assert isinstance(results[0], GenericClass)
    assert results[0].id == f"{issuer_id}.class1"
