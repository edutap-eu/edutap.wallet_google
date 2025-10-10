from edutap.wallet_google.registry import _get_fields_for_name
from edutap.wallet_google.registry import validate_fields_for_name

import pytest


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
    print("\n".join(fields))
    # breakpoint()
    assert "kind" in fields
    assert "id" in fields


def test_validate_fields_for_name():
    assert (
        validate_fields_for_name(
            "LoyaltyObject",
            [
                "kind",
                "id",
            ],
        )
        is True
    )
    assert validate_fields_for_name("LoyaltyObject", ["kind", "id", "spam"]) is False

    assert (
        validate_fields_for_name("LoyaltyObject", ["kind", "id", "imageModulesData/*"])
        is True
    )

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
