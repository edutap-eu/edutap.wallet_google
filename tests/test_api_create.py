def test_api_create(mock_request_response):
    from edutap.wallet_google.api import create
    from edutap.wallet_google.models.primitives.enums import State
    from edutap.wallet_google.registry import lookup_model
    from edutap.wallet_google.session import session_manager

    request_data = mock_request_response(
        "CreateGenericObject", session_manager.url("GenericObject"), "POST"
    )
    result = create("GenericObject", request_data["body"])

    GenericObject = lookup_model("GenericObject")
    assert isinstance(result, GenericObject)
    assert result.id == "3388000000022141777.obj53.test.ycc.edutap"
    assert result.classId == "3388000000022141777.test.ycc.edutap"
    assert result.state == State.ACTIVE
