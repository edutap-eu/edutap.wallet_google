from edutap.wallet_google import api

from edutap.wallet_google.models.passes.retail import LoyaltyObject
from edutap.wallet_google.registry import validate_fields_for_name

import pytest


def test_get_partial_create():
    obj = LoyaltyObject(
        id="issuerid.objectid",
        classId="issuerid.classid",
        state="ACTIVE",
    )

    fields = [
        "kind",
        "id",
    ]
    assert validate_fields_for_name("LoyaltyObject", fields) is True

    created = api.create(obj, fields=fields)
    breakpoint()
    assert created.id == obj.id
    assert created.classId == obj.classId


def test_get_partial_read():
    fields = [
        "id",
    ]
    # assert validate_fields_for_name("GenericObject", fields) is True

    obj = api.read("GenericObject", resource_id="3388000000022141777.obj53.test.ycc.edutap", fields=fields)
    breakpoint()
    assert obj.id == "3388000000022141777.obj53.test.ycc.edutap"
