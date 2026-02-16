import pytest

from edutap.wallet_google.registry import _get_fields_for_name, validate_fields_for_name


@pytest.mark.parametrize(
    "name",
    [
        #    "LoyaltyClass",
        "LoyaltyObject",
        #    "OfferClass",
        #    "OfferObject",
    ],
)
def test_get_fields_for_model(name):
    fields = _get_fields_for_name(name)
    assert "id" in fields
    assert "classId" in fields


def test_validate_fields_for_name():
    assert validate_fields_for_name(
        "LoyaltyObject",
        [
            "id",
            "classId",
        ],
    ) == (True, [])
    assert validate_fields_for_name(
        "LoyaltyObject",
        [
            "id",
            "spam",
        ],
    ) == (
        False,
        ["spam"],
    )

    assert validate_fields_for_name(
        "LoyaltyObject",
        [
            "id",
            "imageModulesData/*",
        ],
    ) == (True, [])

    # assert validate_fields_for_name("LoyaltyObject", ["kind", "id", "imageModulesData(items)"]) is False


# def test_validate_fields_for_name():
#     assert validate_fields_for_name("LoyaltyObject", ["kind", "id", "state"])
#     assert validate_fields_for_name("LoyaltyObject", ["kind", "id", "state", "textModulesData"])
#     assert validate_fields_for_name(
#         "LoyaltyObject",
#         [
#             "kind",
#             "id",
#             "state",
#             "textModulesData",
#             "textModulesData/items",
#             "textModulesData/items/header",
#             "textModulesData/items/body",
#         ],
#     )

#     assert not validate_fields_for_name("Issuer", ["non_existing_field"])
#     assert not validate_fields_for_name("Issuer", ["name", "non_existing_field"])
#     assert not validate_fields_for_name("Issuer", ["name/non_existing_sub_field"])
#     assert not validate_fields_for_name("LoyaltyObject", ["state", "non_existing_field"])
#     assert not validate_fields_for_name(
#         "LoyaltyObject",
#         [
#             "state",
#             "textModulesData",
#             "textModulesData/items",
#             "textModulesData/items/non_existing_sub_field",
#         ],
#     )
