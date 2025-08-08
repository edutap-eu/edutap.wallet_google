# from edutap.wallet_google.models.passes import event_ticket
# from edutap.wallet_google.models.passes import generic
# from edutap.wallet_google.models.passes import loyalty
# from edutap.wallet_google.models.passes import retail
# from edutap.wallet_google.models.passes import transit
from edutap.wallet_google.models.misc import Issuer

from httpx import get

import json


def test_check_modles():
    google_wallet_models = get(
        "https://discovery.googleapis.com/discovery/v1/apis?name=walletobjects"
    )
    data = json.loads(google_wallet_models.text)
    print("\n")
    print("Google Discorvery API response:")
    print(json.dumps(data, indent=2))
    print("\n")
    discoveryRestURL = data.get("items", [{}])[0].get("discoveryRestUrl")
    google_wallet_models = get(discoveryRestURL)
    data = json.loads(google_wallet_models.text)
    print("\n")
    print("Google Wallet Models:")
    print(json.dumps(data, indent=2))
    print("\n")
    print("Checking models...")
    for model_name, attributes in data.get("resources", {}).items():
        print(f"Checking model: {model_name}")
        if model_name == "issuer":
            print(json.dumps(Issuer.model_json_schema(), indent=2))
            print(json.dumps(attributes, indent=2))
            # breakpoint()
            continue
    data
    print("Finished checking models")
