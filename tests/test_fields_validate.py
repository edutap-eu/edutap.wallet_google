import pytest

from edutap.wallet_google.registry import _get_fields_for_name, validate_fields_for_name


@pytest.mark.parametrize(
    "name",
    [
        "LoyaltyClass",
        "LoyaltyObject",
        "OfferClass",
        "OfferObject",
    ],
)
def test_get_fields_for_model(name):
    fields = _get_fields_for_name(name)
    assert "id" in fields


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
