from edutap.wallet_google import api
from edutap.wallet_google.clientpool import client_pool
from edutap.wallet_google.models.bases import Model
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
