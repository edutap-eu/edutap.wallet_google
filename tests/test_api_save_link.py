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
    expected = "https://pay.google.com/gp/v/save/eyJ0eXAiOiAiSldUIiwgImFsZyI6ICJSUzI1NiIsICJraWQiOiAiMTIzNDU2Nzg5MGFiY2RlZjEyMzQ1Njc4OTBhYmNkZWYxMjM0NTY3OCJ9.eyJpc3MiOiAiZWR1dGFwLXRlc3QtZXhhbXBsZUBzb2RpdW0tcmF5LTEyMzQ1Ni5pYW0uZ3NlcnZpY2VhY2NvdW50LmNvbSIsICJhdWQiOiAiZ29vZ2xlIiwgInR5cCI6ICJzYXZldG93YWxsZXQiLCAiaWF0IjogIjE3Mzc1NDEyMDAiLCAicGF5bG9hZCI6IHsib2ZmZXJPYmplY3RzIjogW3siaWQiOiAiMTIzNDU2Nzg5MDEyMzQ1Njc4OS50ZXN0LTIuZWR1dGFwLmV1IiwgImNsYXNzSWQiOiAiMTIzNDU2Nzg5MDEyMzQ1Njc4OS50ZXN0LWNsYXNzLTEuZWR1dGFwLmV1IiwgInN0YXRlIjogIlNUQVRFX1VOU1BFQ0lGSUVEIiwgImhhc0xpbmtlZERldmljZSI6IGZhbHNlLCAiZGlzYWJsZUV4cGlyYXRpb25Ob3RpZmljYXRpb24iOiBmYWxzZSwgIm5vdGlmeVByZWZlcmVuY2UiOiAiTk9USUZJQ0FUSU9OX1NFVFRJTkdTX0ZPUl9VUERBVEVTX1VOU1BFQ0lGSUVEIn1dLCAiZ2VuZXJpY09iamVjdHMiOiBbeyJpZCI6ICIxMjM0NTY3ODkwMTIzNDU2Nzg5LnRlc3QtMS5lZHV0YXAuZXUifV19LCAib3JpZ2lucyI6IFtdLCAiZXhwIjogIiJ9.M5rHck9hIZOCHyIb9waDHsVHIzIQD-Hle4EK-BJYaRnGWeAnG2Gq9jxG9anBWlujRoqwFBsKozaHagGB9AyzpVDbfPJPY7Zm2jRwhe76zzmkSruEr25H1hf_OMxZgpUoyatASikANPPBrayA9-D9nuNThbNCOuSmwFXv4iDdxHHfCzq0iEKiPvw_6fePF7bdPnkv1uE0GA5rseM2olJ830U7xB7wuw7SA84OPoRclMiCvl3RjisTE2PfrkZ0sJlbxM16-aMkAQ-FxlERLoxkeWgSA2yYXuqjEdH0TVbg_b4tGKgQkTXo2TxhaVam4ZqdjYzTkgu9oesPVVae8ZgEtQ"
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
