from edutap.wallet_google.models.misc import Issuer
from edutap.wallet_google.models.passes.bases import ClassModel
from edutap.wallet_google.utils import validate_data_and_convert_to_json

import pytest


def test_api__validate_data_and_convert_to_json__create_mode():
    model = ClassModel(id="12345", enableSmartTap=None)
    _, json = validate_data_and_convert_to_json(ClassModel, model)
    assert json == '{"id":"12345"}'


def test_api__validate_data_and_convert_to_json__existing_mode():
    model = ClassModel(id="12345", enableSmartTap=None)
    _, json = validate_data_and_convert_to_json(ClassModel, model, existing=True)
    assert json == '{"id":"12345","enableSmartTap":null}'


def test_api__validate_data_and_convert_to_json__skip_resource_id_with_none():
    """Test that skip_resource_id=True returns None for identifier when field is None."""
    issuer = Issuer(name="Test Issuer")  # issuerId defaults to None
    identifier, json = validate_data_and_convert_to_json(
        Issuer, issuer, resource_id_key="issuerId", skip_resource_id=True
    )
    assert identifier is None
    assert "issuerId" not in json  # excluded because it's None


def test_api__validate_data_and_convert_to_json__skip_resource_id_raises_when_set():
    """Test that skip_resource_id=True raises ValueError when resource_id is set."""
    issuer = Issuer(name="Test Issuer", issuerId="should-not-be-set")
    with pytest.raises(ValueError) as exc_info:
        validate_data_and_convert_to_json(
            Issuer, issuer, resource_id_key="issuerId", skip_resource_id=True
        )
    assert "must not be set" in str(exc_info.value)
    assert "issuerId" in str(exc_info.value)
