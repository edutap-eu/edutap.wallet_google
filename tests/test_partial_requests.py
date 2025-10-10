from edutap.wallet_google import api
from edutap.wallet_google.models.bases import Model
from typing import Any

import pytest


def test_get_partial_read() -> None:
    fields = [
        "id",
        # "kind",
        "classId",
    ]
    # assert validate_fields_for_name("GenericObject", fields) is True

    obj: Model | dict[str, Any] = api.read(
        "GenericObject",
        resource_id="3388000000022141777.obj53.test.ycc.edutap",
        fields=fields,
    )
    assert isinstance(obj, dict)
    print(obj)
    assert set(fields) == set(obj.keys())
    assert obj["id"] == "3388000000022141777.obj53.test.ycc.edutap"
    assert obj["classId"] == "3388000000022141777.test.ycc.edutap"


@pytest.mark.asyncio
async def test_get_partial_aread() -> None:
    fields = [
        "id",
        "kind",
        "classId",
    ]
    # assert validate_fields_for_name("GenericObject", fields) is True

    obj: Model | dict[str, Any] = await api.aread(
        "GenericObject",
        resource_id="3388000000022141777.obj53.test.ycc.edutap",
        fields=fields,
    )
    assert isinstance(obj, dict)
    print(obj)
    assert set(fields) == set(obj.keys())
    assert obj["id"] == "3388000000022141777.obj53.test.ycc.edutap"
    assert obj["classId"] == "3388000000022141777.test.ycc.edutap"
