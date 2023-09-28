from edutap.wallet_google.models.primitives import enums

import pytest


testdata = [
    (
        "Create",
        "GenericClass",
        "POST",
        {
            "id": "3388000000022141777.test54.ycc.edutap",
            "enableSmartTap": False,
            "multipleDevicesAndHoldersAllowedStatus": enums.MultipleDevicesAndHoldersAllowedStatus.STATUS_UNSPECIFIED,
            "viewUnlockRequirement": enums.ViewUnlockRequirement.VIEW_UNLOCK_REQUIREMENT_UNSPECIFIED,
        },
    ),
    (
        "Create",
        "GenericObject",
        "POST",
        {
            "id": "3388000000022141777.obj53.test.ycc.edutap",
            "classId": "3388000000022141777.test.ycc.edutap",
            "state": enums.State.ACTIVE,
        },
    ),
]


@pytest.mark.parametrize("prefix,name,method,checkdata", testdata)
def test_api_create(mock_request_response, prefix, name, method, checkdata):
    from edutap.wallet_google.api import create
    from edutap.wallet_google.registry import lookup_model
    from edutap.wallet_google.session import session_manager

    request_data = mock_request_response(
        f"{prefix}{name}", session_manager.url(name), method
    )
    result = create(name, request_data["request"]["body"])

    model = lookup_model(name)
    assert isinstance(result, model)
    for key, value in checkdata.items():
        assert getattr(result, key) == value
