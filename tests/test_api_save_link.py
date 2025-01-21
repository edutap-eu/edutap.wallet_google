import datetime
import pytest


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
        "iss": "test@example.com",
        "aud": "google",
        "typ": "savetowallet",
        "iat": "1737115974",
        "exp": "",
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

    claims = api._create_claims(
        "test@example.com",
        [],
        models,
        iat=datetime.datetime(2025, 1, 17, 12, 12, 54, 0, datetime.timezone.utc),
        exp="",
    )

    dumped = claims.model_dump(
        mode="json",
        exclude_unset=False,
        exclude_defaults=False,
        exclude_none=True,
    )
    assert expected == dumped


def test_api_save_link(mock_settings):
    from edutap.wallet_google.settings import ROOT_DIR

    mock_settings.credentials_file = (
        ROOT_DIR / "tests" / "data" / "credentials_fake.json"
    )

    from edutap.wallet_google import api

    link = api.save_link(
        [
            api.new(
                "Reference",
                {
                    "id": "1234567890123456789.test-1.edutap.eu",
                    "model_name": "GenericObject",
                },
            ),
            api.new(
                "OfferObject",
                {
                    "id": "1234567890123456789.test-2.edutap.eu",
                    "classId": "1234567890123456789.test-class-1.edutap.eu",
                },
            ),
        ],
        iat=datetime.datetime(2025, 1, 22, 10, 20, 0, 0, datetime.timezone.utc),
    )
    expected = "https://pay.google.com/gp/v/save/eyJ0eXAiOiAiSldUIiwgImFsZyI6ICJSUzI1NiIsICJraWQiOiAiMTIzNDU2Nzg5MGFiY2RlZjEyMzQ1Njc4OTBhYmNkZWYxMjM0NTY3OCJ9.eyJpc3MiOiAiZWR1dGFwLXRlc3QtZXhhbXBsZUBzb2RpdW0tcmF5LTEyMzQ1Ni5pYW0uZ3NlcnZpY2VhY2NvdW50LmNvbSIsICJhdWQiOiAiZ29vZ2xlIiwgInR5cCI6ICJzYXZldG93YWxsZXQiLCAiaWF0IjogIjE3Mzc1NDEyMDAiLCAiZXhwIjogIiIsICJwYXlsb2FkIjogeyJvZmZlck9iamVjdHMiOiBbeyJpZCI6ICIxMjM0NTY3ODkwMTIzNDU2Nzg5LnRlc3QtMi5lZHV0YXAuZXUiLCAiY2xhc3NJZCI6ICIxMjM0NTY3ODkwMTIzNDU2Nzg5LnRlc3QtY2xhc3MtMS5lZHV0YXAuZXUiLCAic3RhdGUiOiAiU1RBVEVfVU5TUEVDSUZJRUQiLCAiaGFzTGlua2VkRGV2aWNlIjogZmFsc2UsICJkaXNhYmxlRXhwaXJhdGlvbk5vdGlmaWNhdGlvbiI6IGZhbHNlLCAibm90aWZ5UHJlZmVyZW5jZSI6ICJOT1RJRklDQVRJT05fU0VUVElOR1NfRk9SX1VQREFURVNfVU5TUEVDSUZJRUQifV0sICJnZW5lcmljT2JqZWN0cyI6IFt7ImlkIjogIjEyMzQ1Njc4OTAxMjM0NTY3ODkudGVzdC0xLmVkdXRhcC5ldSJ9XX0sICJvcmlnaW5zIjogW119.OJcaFwQ9XlKvMb0t-aokejx39zeHiPMIkA5EQSU7oPXgFy740OHFN0-vsw-8ABMc4HB-ZipuH6ZN1MhbOc1baabPl4s8XLU_Z43NMUXmKKz2KExt2F7qiuy_04aeFZQVBGoZOCQicjD_qrh6YqGYHdQFkcjtOAAdy0JPwVsfdiowTdDv4EdH2eZXLvE3bKYeu1rvD6oBS5xCIDwu77t3DurrKYf1yYfOL4YpnNAwru-o7MM_J-FKzVur6wJ0xQgYCP_UtX8PxHoj2-YXQ0yXlypgw8Vpo069hcrOVyQaRdrFEVf_TKi6IBLpPr6zxk19NhmJ9qjwIUygMEkyfRf3Mw"
    assert link == expected


def test__convert_str_or_datetime_to_str__timestamp():
    from edutap.wallet_google.api import _convert_str_or_datetime_to_str

    dt = datetime.datetime(2021, 1, 1, 12, 0, 0, 0, datetime.timezone.utc)
    expected = "1609502400"

    assert _convert_str_or_datetime_to_str(dt) == expected


def test__convert_str_or_datetime_to_str__str_int_lt_zero():
    from edutap.wallet_google.api import _convert_str_or_datetime_to_str

    with pytest.raises(ValueError):
        _convert_str_or_datetime_to_str("-1")


def test__convert_str_or_datetime_to_str__str_int_tr_4bytes():
    from edutap.wallet_google.api import _convert_str_or_datetime_to_str

    with pytest.raises(ValueError):
        _convert_str_or_datetime_to_str(f"{2**32 + 1}")


def test__convert_str_or_datetime_to_str__not_decimal():
    from edutap.wallet_google.api import _convert_str_or_datetime_to_str

    with pytest.raises(ValueError):
        _convert_str_or_datetime_to_str("x 100")
