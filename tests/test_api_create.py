from edutap.wallet_google.models.datatypes import enums

import pytest
import respx


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


@respx.mock
@pytest.mark.parametrize("prefix,name,method,checkdata", testdata)
def test_api_create(mock_request_response, prefix, name, method, checkdata):
    from edutap.wallet_google.api import create
    from edutap.wallet_google.api import new
    from edutap.wallet_google.clientpool import client_pool
    from edutap.wallet_google.registry import lookup_model_by_name

    request_data = mock_request_response(
        f"{prefix}{name}", client_pool.url(name), method
    )
    data = new(name, request_data["request"]["body"])
    result = create(data)

    model = lookup_model_by_name(name)
    assert isinstance(result, model)
    for key, value in checkdata.items():
        assert getattr(result, key) == value


@respx.mock
def test_api_create_issuer_without_issuer_id(mock_session):
    """Test that Issuer create works with pass_resource_id_on_create=False."""
    from edutap.wallet_google.api import create
    from edutap.wallet_google.clientpool import client_pool
    from edutap.wallet_google.models.misc import Issuer

    import httpx
    import json

    url = client_pool.url("Issuer")

    # Capture the request to verify payload
    captured_request = None

    def capture_request(request):
        nonlocal captured_request
        captured_request = request
        return httpx.Response(200, json={"issuerId": "123", "name": "Test"})

    respx.post(url).mock(side_effect=capture_request)

    # Create Issuer without issuerId (it's optional and None by default)
    issuer = Issuer(name="Test Issuer")
    create(issuer)

    # Verify issuerId was NOT in the request payload (excluded because it's None)
    request_body = json.loads(captured_request.content)
    assert "issuerId" not in request_body
    assert request_body["name"] == "Test Issuer"


def test_api_create_issuer_raises_when_issuer_id_set(mock_session):
    """Test that Issuer create raises ValueError when issuerId is set."""
    from edutap.wallet_google.api import create
    from edutap.wallet_google.models.misc import Issuer

    # Try to create Issuer WITH issuerId set (should raise)
    issuer = Issuer(name="Test Issuer", issuerId="should-not-be-set")

    with pytest.raises(ValueError) as exc_info:
        create(issuer)

    assert "must not be set" in str(exc_info.value)
    assert "issuerId" in str(exc_info.value)


def test_api_create_jwt_resource_is_not_allowed(mock_session):
    """JwtResource is not a CRUD resource, and create() must say so.

    It is registered so the model can be looked up by name, and its url_part
    points at the jwt.insert endpoint. That endpoint is not implemented, and
    two things stand in the way of it ever working through create():
    JwtResource has no id, and the endpoint answers with {saveUri, resources}
    while create() parses the response with the model it sent.

    Without this guard the first of the two wins and the caller gets
    "AttributeError: 'JwtResource' object has no attribute 'id'" out of
    utils.py, which says nothing about the real cause.

    jwt.insert is deliberately not wanted - the JWT length ceiling it would
    solve is already handled by putting a Reference into the JWT rather than
    the full object.
    """
    from edutap.wallet_google.api import create
    from edutap.wallet_google.models.misc import JwtResource

    with pytest.raises(ValueError) as exc_info:
        create(JwtResource(jwt="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.e30.signature"))

    assert "not allowed" in str(exc_info.value)
    assert "JwtResource" in str(exc_info.value)
