from freezegun import freeze_time


def test_create_payload():

    from edutap.wallet_google import api

    payload = api._create_payload(
        [
            api.new(
                "Reference", {"id": "test-1.edutap.eu", "model_name": "GenericObject"}
            ),
            api.new(
                "OfferObject",
                {"id": "test-2.edutap.eu", "classId": "test-class-1.edutap.eu"},
            ),
        ]
    )
    expected = '{"offerObjects":[{"id":"test-2.edutap.eu","classId":"test-class-1.edutap.eu","state":"STATE_UNSPECIFIED","hasLinkedDevice":false,"disableExpirationNotification":false,"notifyPreference":"NOTIFICATION_SETTINGS_FOR_UPDATES_UNSPECIFIED"}],"genericObjects":[{"id":"test-1.edutap.eu"}]}'
    assert payload.model_dump_json(exclude_none=True) == expected


@freeze_time("2025-01-17 12:54:00")
def test_create_claims():

    from edutap.wallet_google import api

    models = [
        api.new("Reference", {"id": "test-1.edutap.eu", "model_name": "GenericObject"}),
        api.new(
            "OfferObject",
            {"id": "test-2.edutap.eu", "classId": "test-class-1.edutap.eu"},
        ),
    ]
    expected = {
        "iss": "123456789",
        "aud": "google",
        "typ": "savettowallet",
        "iat": "1737118440",
        "payload": {
            "offerObjects": [
                {
                    "id": "test-2.edutap.eu",
                    "classId": "test-class-1.edutap.eu",
                    "state": "STATE_UNSPECIFIED",
                    "hasLinkedDevice": False,
                    "disableExpirationNotification": False,
                    "notifyPreference": "NOTIFICATION_SETTINGS_FOR_UPDATES_UNSPECIFIED",
                }
            ],
            "genericObjects": [{"id": "test-1.edutap.eu"}],
        },
        "origins": [],
    }

    claims = api._create_claims("123456789", [], models)

    dumped = claims.model_dump(
        mode="json",
        exclude_unset=False,
        exclude_defaults=False,
        exclude_none=True,
    )
    assert expected == dumped


@freeze_time("2025-01-17 12:54:00")
def test_api_save_link(mock_settings):
    from edutap.wallet_google.settings import ROOT_DIR

    mock_settings.issuer_id = "1234567890123456789"
    mock_settings.credentials_file = (
        ROOT_DIR / "tests" / "data" / "credentials_fake.json"
    )

    from edutap.wallet_google import api

    link = api.save_link(
        [
            api.new(
                "Reference", {"id": "test-1.edutap.eu", "model_name": "GenericObject"}
            ),
            api.new(
                "OfferObject",
                {"id": "test-2.edutap.eu", "classId": "test-class-1.edutap.eu"},
            ),
        ]
    )
    assert (
        link
        == "https://pay.google.com/gp/v/save/eyJ0eXAiOiAiSldUIiwgImFsZyI6ICJSUzI1NiIsICJraWQiOiAiMTIzNDU2Nzg5MGFiY2RlZjEyMzQ1Njc4OTBhYmNkZWYxMjM0NTY3OCJ9.eyJpc3MiOiAiZWR1dGFwLXRlc3QtZXhhbXBsZUBzb2RpdW0tcmF5LTEyMzQ1Ni5pYW0uZ3NlcnZpY2VhY2NvdW50LmNvbSIsICJhdWQiOiAiZ29vZ2xlIiwgInR5cCI6ICJzYXZldHRvd2FsbGV0IiwgImlhdCI6ICIxNzM3MTE4NDQwIiwgInBheWxvYWQiOiB7Im9mZmVyT2JqZWN0cyI6IFt7ImlkIjogInRlc3QtMi5lZHV0YXAuZXUiLCAiY2xhc3NJZCI6ICJ0ZXN0LWNsYXNzLTEuZWR1dGFwLmV1IiwgInN0YXRlIjogIlNUQVRFX1VOU1BFQ0lGSUVEIiwgImhhc0xpbmtlZERldmljZSI6IGZhbHNlLCAiZGlzYWJsZUV4cGlyYXRpb25Ob3RpZmljYXRpb24iOiBmYWxzZSwgIm5vdGlmeVByZWZlcmVuY2UiOiAiTk9USUZJQ0FUSU9OX1NFVFRJTkdTX0ZPUl9VUERBVEVTX1VOU1BFQ0lGSUVEIn1dLCAiZ2VuZXJpY09iamVjdHMiOiBbeyJpZCI6ICJ0ZXN0LTEuZWR1dGFwLmV1In1dfSwgIm9yaWdpbnMiOiBbXX0.X5nE4Zh4kvxGZ4LxnEw8_9i2tCq-JJUmSCRxpf8ckQJVNumsA_uQze0uyuCPTBSVsdHcnMxozFdiCktrwIdvBYDjSLf91acoADMtY1n-HIPbCexlpTpHgyDpyC8giVx27lAvkjaDtHzvEoJ1nAkwh-_-322uKwEWOllR_voV162lNLMIE5QY2eDJ9yfcFa5LXqxSW64UDTZSYX0DsJtGf-Oa1HOgnG77D6RZfMYUq18duNmcBp5wREVrE27vPjnVRC2kEsrWfQNw4gkN_aSp6ZhEAG-exQqUQQXeR7nPqYm-DM7uVOCh8pbk8WqwA7fKcsZIRK8dsWnqnDuNdwP7Gw"
    )
