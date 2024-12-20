import pytest


def test_reference_validator_missing():
    from edutap.wallet_google.models.passes.bases import Reference

    import pydantic

    with pytest.raises(pydantic.ValidationError):
        Reference(id="1234")


def test_reference_validator_both():
    from edutap.wallet_google.models.passes.bases import Reference
    from edutap.wallet_google.models.passes.generic import GenericObject

    import pydantic

    with pytest.raises(pydantic.ValidationError):
        Reference(id="1234", model_name="GenericObject", model_type=GenericObject)
