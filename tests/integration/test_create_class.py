import pytest
import uuid


text_modules_data = [
    {
        "Body": "test header",
        "body": "test body",
        "localizedHeader": {
            "defaultValue": {
                "language": "en",
                "value": "test header",
            },
            "translatedValues": [
                {
                    "language": "de",
                    "value": "Test Kopfzeile",
                }
            ],
        },
        "localizedBody": {
            "defaultValue": {
                "language": "en",
                "value": "test body",
            },
            "translatedValues": [
                {
                    "language": "de",
                    "value": "Test Textkörper",
                }
            ],
        },
    }
]

params_for_create = [
    (
        "GenericClass",
        {
            "textModulesData": text_modules_data,
        },
    ),
]


@pytest.mark.integration
@pytest.mark.parametrize("class_type,class_data", params_for_create)
def test_class_creation(class_type, class_data):
    from edutap.wallet_google.api import create
    from edutap.wallet_google.api import session_manager

    class_data[
        "id"
    ] = f"{session_manager.settings.issuer_id}.{uuid.uuid4()}.test.wallet_google.edutap"
    result = create(class_type, class_data)
    assert result is not None
