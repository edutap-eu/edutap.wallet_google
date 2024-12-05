from edutap.wallet_google.api import _validate_data_and_convert_to_json
from edutap.wallet_google.models.bases import GoogleWalletClassModel


def test_api__validate_data_and_convert_to_json__create_mode():
    model = GoogleWalletClassModel(id="12345", enableSmartTap=None)
    _, json = _validate_data_and_convert_to_json(GoogleWalletClassModel, model)
    assert json == '{"id":"12345"}'


def test_api__validate_data_and_convert_to_json__existing_mode():
    model = GoogleWalletClassModel(id="12345", enableSmartTap=None)
    _, json = _validate_data_and_convert_to_json(
        GoogleWalletClassModel, model, existing=True
    )
    assert json == '{"id":"12345","enableSmartTap":null}'
