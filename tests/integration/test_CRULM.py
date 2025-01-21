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
        "Generic",
        {
            "textModulesData": text_modules_data,
        },
        {
            "state": "INACTIVE",
            "cardTitle": {
                "defaultValue": {
                    "language": "en",
                    "value": "test card title",
                },
            },
            "header": {
                "defaultValue": {
                    "language": "en",
                    "value": "test header",
                },
            },
        },
    ),
    (
        "GiftCard",
        {
            "issuerName": "test issuer",
            "reviewStatus": "DRAFT",
            "textModulesData": text_modules_data,
        },
        {
            "state": "INACTIVE",
            "cardNumber": "test card number 1234",
        },
    ),
    (
        "Loyalty",
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
                },
            },
            "reviewStatus": "DRAFT",
            "textModulesData": text_modules_data,
        },
        {
            "state": "INACTIVE",
        },
    ),
    (
        "Offer",
        {
            "issuerName": "test issuer",
            "reviewStatus": "DRAFT",
            "textModulesData": text_modules_data,
            "title": "test title",
            "redemptionChannel": "ONLINE",
            "provider": "test provider",
        },
        {
            "state": "INACTIVE",
        },
    ),
]


@pytest.mark.integration
@pytest.mark.parametrize("type_base,class_data,object_data", params_for_create)
def test_class_object_cru(type_base, class_data, object_data, integration_test_id):
    from edutap.wallet_google.api import create
    from edutap.wallet_google.api import listing
    from edutap.wallet_google.api import message
    from edutap.wallet_google.api import new
    from edutap.wallet_google.api import read
    from edutap.wallet_google.api import session_manager
    from edutap.wallet_google.api import update
    from edutap.wallet_google.registry import lookup_metadata_by_name

    import time

    class_type = f"{type_base}Class"
    object_type = f"{type_base}Object"

    ############################
    # test class
    class_base = f"{integration_test_id}.{class_type}.test_CRU.wallet_google.edutap"
    class_data["id"] = f"{session_manager.settings.test_issuer_id}.{class_base}"

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
    if type_base != "Generic":
        # generic has no reviewState
        result_read.reviewStatus = "UNDER_REVIEW"
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
    result_list = [
        x
        for x in listing(
            name=class_type, issuer_id=session_manager.settings.test_issuer_id
        )
    ]
    assert len(result_list) > 0

    ############################
    # test object
    object_data["classId"] = class_data["id"]
    object_base = f"{integration_test_id}.{object_type}.test_CRU.wallet_google.edutap"
    object_data["id"] = f"{session_manager.settings.test_issuer_id}.{object_base}"
    odata = new(object_type, object_data)

    # create
    oresult_create = create(odata)
    assert oresult_create is not None
    assert oresult_create.state == "INACTIVE"

    # relax - not sure if this is necessary
    time.sleep(0.05)

    # read
    oresult_read = read(name=object_type, resource_id=object_data["id"])
    assert oresult_read is not None
    assert oresult_read.state == "INACTIVE"

    # update
    oresult_read.state = "ACTIVE"
    oresult_updated = update(oresult_read)
    assert oresult_updated is not None
    assert oresult_updated.state == "ACTIVE"

    # read after update
    oresult_read = read(name=object_type, resource_id=object_data["id"])
    assert oresult_read is not None
    assert oresult_read.state == "ACTIVE"

    # list all
    result_list = [x for x in listing(name=object_type, resource_id=class_data["id"])]
    assert len(result_list) == 1

    model_metadata = lookup_metadata_by_name(class_type)
    if model_metadata["can_message"]:
        # send message
        result_message = message(
            name=object_type,
            resource_id=object_data["id"],
            message={
                "messageType": "TEXT",
                "id": "test-message",
                "header": "test header",
                "body": "test body",
            },
        )
        assert result_message is not None
        assert result_message.id == object_data["id"]
