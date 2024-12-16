from fastapi import FastAPI
from fastapi.testclient import TestClient


# this callback data can be verified given the credentials.json from demo.edutap.eu is provided.
real_callback_data = {
    "signature": "MEYCIQCyuBQo/Dao7yUBDUWK12ATFBDkUfJUnropjOaPbPiKEwIhAKXNiVrbNmydpEVIxXRz5z36f8HV2Meq/Td6tqt2+DYO",
    "intermediateSigningKey": {
        "signedKey": '{"keyValue":"MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE3JpSX3AU53vH+IpWBdsbqrL7Ey67QSERsDUztFt8q7t7PzVkh14SeYeokI1zSZiVAWnx4tXD1tCPbrvfFGB8OA\\u003d\\u003d","keyExpiration":"1735023986000"}',
        "signatures": [
            "MEUCIQD3IBTpRM45gpno9Remtx/FiDCOJUp45+C+Qzw6IrgphwIgJijXISc+Ft8Sj9eXNowzuYyXyWlgKAE+tVnN24Sek5M="
        ],
    },
    "protocolVersion": "ECv2SigningOnly",
    "signedMessage": '{"classId":"3388000000022141777.pass.gift.dev.edutap.eu","objectId":"3388000000022141777.9fd4e525-777c-4e0d-878a-b7993e211997","eventType":"save","expTimeMillis":1734366082269,"count":1,"nonce":"c1359b53-f2bb-4e8f-b392-9a560a21a9a0"}',
}


def test_callback():
    ...
    from edutap.wallet_google.models.handlers import CallbackData
    from edutap.wallet_google.session import session_manager

    settings = session_manager.settings
    settings.callback_verify_signature = False
    callback_data = CallbackData(**real_callback_data)

    from edutap.wallet_google.handlers.fastapi import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    client.post("/googlewallet/callback", json=callback_data.model_dump(mode="json"))
    del session_manager._settings
