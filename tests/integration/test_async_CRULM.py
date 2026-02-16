"""Integration tests for async API CRUD operations against real Google Wallet API."""

import asyncio

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
                    "uri": "https://avatars.githubusercontent.com/u/142002169?s=48&v=4",
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
@pytest.mark.asyncio
@pytest.mark.parametrize("type_base,class_data,object_data", params_for_create)
async def test_async_class_object_cru(
    type_base, class_data, object_data, integration_test_id
):
    from edutap.wallet_google import api
    from edutap.wallet_google.clientpool import client_pool
    from edutap.wallet_google.registry import lookup_metadata_by_name

    class_type = f"{type_base}Class"
    object_type = f"{type_base}Object"

    ############################
    # test class
    class_base = (
        f"{integration_test_id}.{class_type}.test_async_CRU.wallet_google.edutap"
    )
    class_data["id"] = f"{client_pool.settings.test_issuer_id}.{class_base}"

    data = api.new(class_type, class_data)

    # create
    result_create = await api.acreate(data)
    assert result_create is not None
    assert result_create.textModulesData[0].id == class_data["textModulesData"][0]["id"]
    assert (
        result_create.textModulesData[0].header
        == class_data["textModulesData"][0]["header"]
    )

    # relax - not sure if this is necessary
    await asyncio.sleep(0.05)

    # read
    result_read = await api.aread(name=class_type, resource_id=class_data["id"])
    assert result_read is not None
    assert (
        result_read.textModulesData[0].body == class_data["textModulesData"][0]["body"]
    )
    if "reviewStatus" in class_data:
        assert result_read.reviewStatus == class_data["reviewStatus"]

    # update - full
    result_read.textModulesData[0].body = "updated body async"
    if type_base != "Generic":
        # generic has no reviewState
        result_read.reviewStatus = "UNDER_REVIEW"
    result_updated = await api.aupdate(result_read)
    assert result_updated is not None
    assert result_updated.textModulesData[0].body == "updated body async"

    # read after update
    result_read = await api.aread(name=class_type, resource_id=class_data["id"])
    assert result_read is not None
    assert result_read.textModulesData[0].body == "updated body async"

    model_metadata = lookup_metadata_by_name(class_type)
    if model_metadata["can_message"]:
        # send message to all
        result_message = await api.amessage(
            name=class_type,
            resource_id=class_data["id"],
            message={
                "messageType": "TEXT",
                "id": "test-message-async",
                "header": "test header async",
                "body": "test body async",
            },
        )
        assert result_message is not None
        assert result_message.id == class_data["id"]

    # list all
    result_list = []
    async for x in api.alisting(
        name=class_type, issuer_id=client_pool.settings.test_issuer_id
    ):
        result_list.append(x)
    assert len(result_list) > 0

    ############################
    # test object
    object_data["classId"] = class_data["id"]
    object_base = (
        f"{integration_test_id}.{object_type}.test_async_CRU.wallet_google.edutap"
    )
    object_data["id"] = f"{client_pool.settings.test_issuer_id}.{object_base}"
    odata = api.new(object_type, object_data)

    # create
    oresult_create = await api.acreate(odata)
    assert oresult_create is not None
    assert oresult_create.state == "INACTIVE"

    # relax - not sure if this is necessary
    await asyncio.sleep(0.05)

    # read
    oresult_read = await api.aread(name=object_type, resource_id=object_data["id"])
    assert oresult_read is not None
    assert oresult_read.state == "INACTIVE"

    # update
    oresult_read.state = "ACTIVE"
    oresult_updated = await api.aupdate(oresult_read)
    assert oresult_updated is not None
    assert oresult_updated.state == "ACTIVE"

    # read after update
    oresult_read = await api.aread(name=object_type, resource_id=object_data["id"])
    assert oresult_read is not None
    assert oresult_read.state == "ACTIVE"

    # list all
    result_list = []
    async for x in api.alisting(name=object_type, resource_id=class_data["id"]):
        result_list.append(x)
    assert len(result_list) == 1

    model_metadata = lookup_metadata_by_name(class_type)
    if model_metadata["can_message"]:
        # send message
        result_message = await api.amessage(
            name=object_type,
            resource_id=object_data["id"],
            message={
                "messageType": "TEXT",
                "id": "test-message-async",
                "header": "test header async",
                "body": "test body async",
            },
        )
        assert result_message is not None
        assert result_message.id == object_data["id"]

    # Clean up async clients to avoid event loop closed errors
    await client_pool.aclose_all_clients()
