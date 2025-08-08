# from edutap.wallet_google.models.passes import event_ticket
# from edutap.wallet_google.models.passes import generic
# from edutap.wallet_google.models.passes import loyalty
# from edutap.wallet_google.models.passes import retail
# from edutap.wallet_google.models.passes import transit
from edutap.wallet_google.models.misc import Issuer

from httpx import get

import json


def test_check_modles():
    discovery_api_data = get(
        "https://discovery.googleapis.com/discovery/v1/apis?name=walletobjects"
    )
    data = json.loads(discovery_api_data.text)
    print("\n")
    print("Google Discorvery API response:")
    print(json.dumps(data, indent=2))
    print("\n")
    assert len(data["items"]) == 1, "Discovery API response showed more than one API Description"
    assert data["items"][0]["version"] == "v1", "Discovery API response showed a different version than v1"
    assert data["items"][0]["id"] == "walletobjects:v1", "Discovery API response showed a different ID than walletobjects:v1"
    assert data["items"][0]["name"] == "walletobjects"
    assert data["items"][0]["title"] == "Google Wallet API", "Discovery API response showed a different title than Google Wallet API"

    discoveryRestURL = data.get("items", [{}])[0].get("discoveryRestUrl")
    google_wallet_api_data = get(discoveryRestURL)
    data = json.loads(google_wallet_api_data.text)
    assert data["version"] == "v1", "Google Wallet API response showed a different version than v1"
    assert data["id"] == "walletobjects:v1", "Google Wallet API response showed a different ID than walletobjects:v1"
    assert data["title"] == "Google Wallet API", "Google Wallet API response showed a different title than Google Wallet API"
    assert data["protocol"] == "rest", "Google Wallet API response showed a different protocol than rest"
    print("\n")
    print(data.keys())
    # print(json.dumps(data["schemas"], indent=2))
    print("\n")
    print("Google Wallet Models:")
    # print(json.dumps(data, indent=2))
    print("\n")
    print("Checking models...")
    for model_name, attributes in data.get("schemas", {}).items():
        print(f"Checking model: {model_name}")
        if model_name == "Issuer":
            properties_schema = set(Issuer.model_json_schema().get("properties").keys())
            properties_model = set(attributes.get("properties", {}).keys())
            assert properties_schema == properties_model, f"Properties mismatch for model {model_name}"
            print(f"Model {model_name} properties match.")
    data
    print("Finished checking models")
