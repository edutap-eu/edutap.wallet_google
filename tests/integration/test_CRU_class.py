import pytest


text_modules_data = [
    {
        "id": "test_without_localization",
        "header": "test header",
        "body": "test body",
    },
    {
        "id": "test_with_localization",
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
    },
]

params_for_create = [
    (
        "GenericClass",
        {
            "textModulesData": text_modules_data,
        },
    ),
    (
        "GiftCardClass",
        {
            "issuerName": "test issuer",
            "reviewStatus": "DRAFT",
            "textModulesData": text_modules_data,
        },
    ),
    (
        "LoyaltyClass",
        {
            "issuerName": "test issuer",
            "programName": "test program",
            "programLogo": {
                "sourceUri": {
                    "uri": "https://edutap.eu/static/3d642ea43b0bc1fb150510749f6c2333/084c2/eugloh-white.webp",
                },
                "contentDescription": {
                    "defaultValue": {
                        "language": "en",
                        "value": "test logo",
                    },
                }
            },
            "reviewStatus": "DRAFT",
            "textModulesData": text_modules_data,
        },
    ),
    (
        "OfferClass",
        {
            "issuerName": "test issuer",
            "reviewStatus": "DRAFT",
            "textModulesData": text_modules_data,
            "title": "test title",
            "redemptionChannel": "ONLINE",
            "provider": "test provider",
        },
    ),
]


@pytest.mark.integration
@pytest.mark.parametrize("class_type,class_data", params_for_create)
def test_class_cru(class_type, class_data, integration_test_id):
    from edutap.wallet_google.api import create
    from edutap.wallet_google.api import listing
    from edutap.wallet_google.api import message
    from edutap.wallet_google.api import new
    from edutap.wallet_google.api import read
    from edutap.wallet_google.api import session_manager
    from edutap.wallet_google.api import update
    from edutap.wallet_google.registry import lookup_metadata_by_name

    import time

    class_data["id"] = (
        f"{session_manager.settings.issuer_id}.{integration_test_id}.{class_type}.test_CRU.wallet_google.edutap"
    )
    data = new(class_type, class_data)

    # create
    result_create = create(data)
    assert result_create is not None
    assert result_create.textModulesData[0].id == class_data["textModulesData"][0]["id"]
    assert (
        result_create.textModulesData[0].header
        == class_data["textModulesData"][0]["header"]
    )

    # relax - not sure if this is necessary
    time.sleep(0.05)

    # read
    result_read = read(name=class_type, resource_id=class_data["id"])
    assert result_read is not None
    assert (
        result_read.textModulesData[0].body == class_data["textModulesData"][0]["body"]
    )
    if "reviewStatus" in class_data:
        assert result_read.reviewStatus == class_data["reviewStatus"]

    # update - full
    result_read.textModulesData[0].body = "updated body"
    result_updated = update(result_read)
    assert result_updated is not None
    assert result_updated.textModulesData[0].body == "updated body"

    # read after update
    result_read = read(name=class_type, resource_id=class_data["id"])
    assert result_read is not None
    assert result_read.textModulesData[0].body == "updated body"

    model_metadata = lookup_metadata_by_name(class_type)
    if model_metadata["can_message"]:
        # send message to all
        result_message = message(
            name=class_type,
            resource_id=class_data["id"],
            message={
                "messageType": "TEXT",
                "id": "test-message",
                "header": "test header",
                "body": "test body",
            },
        )
        assert result_message is not None
        assert result_message.id == class_data["id"]

    # list all
    result_list = [x for x in listing(name=class_type)]
    assert result_list is not None
    assert len(result_list) > 0
