from edutap.wallet_google.models.passes.bases import ClassModel
from edutap.wallet_google.utils import validate_data_and_convert_to_json


def test_api__validate_data_and_convert_to_json__create_mode():
    model = ClassModel(id="12345", enableSmartTap=None)
    _, json = validate_data_and_convert_to_json(ClassModel, model)
    assert json == '{"id":"12345"}'


def test_api__validate_data_and_convert_to_json__existing_mode():
    model = ClassModel(id="12345", enableSmartTap=None)
    _, json = validate_data_and_convert_to_json(ClassModel, model, existing=True)
    assert json == '{"id":"12345","enableSmartTap":null}'
