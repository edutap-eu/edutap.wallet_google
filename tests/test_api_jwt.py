import datetime

import pytest


def test_create_payload():

    from edutap.wallet_google import api
    from edutap.wallet_google.api import _create_payload

    payload = _create_payload(
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
    from edutap.wallet_google.api import _create_claims

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

    claims = _create_claims(
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


def test_api_save_link():
    import base64
    import json

    from edutap.wallet_google.settings import ROOT_DIR

    credentials_file = ROOT_DIR / "tests" / "data" / "credentials_fake.json"
    with open(credentials_file) as fd:
        credentials = json.load(fd)

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
        credentials=credentials,
    )

    # Verify the URL structure
    assert link.startswith("https://pay.google.com/gp/v/save/")

    # Extract and decode the JWT to verify its structure
    jwt_token = link.replace("https://pay.google.com/gp/v/save/", "")
    parts = jwt_token.split(".")
    assert len(parts) == 3  # header.payload.signature

    # Decode and verify header
    header_decoded = base64.urlsafe_b64decode(parts[0] + "==")
    header = json.loads(header_decoded)
    assert header["typ"] == "JWT"
    assert header["alg"] == "RS256"
    assert header["kid"] == credentials["private_key_id"]

    # Decode and verify payload
    payload_decoded = base64.urlsafe_b64decode(parts[1] + "==")
    payload = json.loads(payload_decoded)
    assert (
        payload["iss"]
        == "edutap-test-example@sodium-ray-123456.iam.gserviceaccount.com"
    )
    assert payload["aud"] == "google"
    assert payload["typ"] == "savetowallet"
    assert payload["iat"] == "1737541200"
    assert payload["exp"] == ""
    assert payload["origins"] == []

    # Verify payload content
    assert len(payload["payload"]["offerObjects"]) == 1
    assert (
        payload["payload"]["offerObjects"][0]["id"]
        == "1234567890123456789.test-2.edutap.eu"
    )
    assert (
        payload["payload"]["offerObjects"][0]["classId"]
        == "1234567890123456789.test-class-1.edutap.eu"
    )
    assert len(payload["payload"]["genericObjects"]) == 1
    assert (
        payload["payload"]["genericObjects"][0]["id"]
        == "1234567890123456789.test-1.edutap.eu"
    )

    # Verify signature exists (3rd part should be non-empty base64)
    assert len(parts[2]) > 0


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
