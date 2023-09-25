def test_api_create(mock_session):
    from edutap.wallet_google.api import create
    from edutap.wallet_google.registry import lookup_model
    from edutap.wallet_google.session import session_manager

    url = session_manager.url("GenericObject")
    request_data = {
        "id": "1234.obj.test",
        "classId": "1234.class.test",
        "state": "ACTIVE",
        "cardTitle": {
            "defaultValue": {
                "value": "YCC Foobar",
                "language": "en",
            },
        },
        "header": {
            "defaultValue": {
                "value": "Heading YCC Foobar bar",
                "language": "en",
            },
        },
    }
    response_data = request_data
    mock_session.register_uri("POST", url, json=response_data, status_code=200)

    result = create("GenericObject", request_data)

    GenericObject = lookup_model("GenericObject")
    assert isinstance(result, GenericObject)
    assert result.id == "1234.obj.test"
    assert result.classId == "1234.class.test"
