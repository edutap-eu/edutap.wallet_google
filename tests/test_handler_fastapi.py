from fastapi import FastAPI
from fastapi.testclient import TestClient
from freezegun import freeze_time

from edutap.wallet_google.plugins import add_plugin, remove_plugins


# this callback data can be verified given the credentials.json from demo.edutap.eu is provided.
real_callback_data = {
    "signature": "MEUCIQC+xKva1ydmNwJJiP2HJJWsteUe02ztTDKExzcWIpmlywIgJwD4HUYvZJg/cr1OL21vVKr0b2ZXt79NblCQ1V18zsc=",
    "intermediateSigningKey": {
        "signedKey": '{"keyValue":"MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEKb256ssDdmf7DokZ7jsMtAvjiTX2HF1ay8QR1sSA+gFpC/ChhRwVdMEVJTaoAP1MIH38QWtqShiQ63zROaKtgQ\\u003d\\u003d","keyExpiration":"1759996807000"}',
        "signatures": [
            "MEUCIDd7rXh7qgJZ7YSlQiXG2zOdZUT5XlMSUPu3RfyV3p2CAiEApxrIwTmRVig93FVJUC6bSWdQXMqata5sHenKsVYreUk="
        ],
    },
    "protocolVersion": "ECv2SigningOnly",
    "signedMessage": '{"classId":"3388000000022141777.lib.edutap.eu","objectId":"3388000000022141777.6b4cbd15-0de7-4fe8-95f6-995a51b4595e.object","eventType":"del","expTimeMillis":1759331348143,"count":1,"nonce":"1a9e3df0-ec10-4a17-8b39-89d2d7f48e3b"}',
}


@freeze_time("2025-10-01 12:00:00")
def test_callback_disabled_signature_check_OK(mock_settings, dummy_plugins):
    from edutap.wallet_google.models.handlers import CallbackData

    # test callback handler without signature check
    mock_settings.handler_callback_verify_signature = "1"

    callback_data = CallbackData(**real_callback_data)

    from edutap.wallet_google.handlers.fastapi import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    resp = client.post(
        "/wallet/google/callback", json=callback_data.model_dump(mode="json")
    )
    assert resp.status_code == 200
    assert resp.json() == {"status": "success"}


@freeze_time("2025-10-01 12:00:00")
def test_callback_disabled_signature_check_ERROR(mock_settings, dummy_plugins):
    from edutap.wallet_google.models.handlers import CallbackData

    # test callback handler without signature check
    mock_settings.handler_callback_verify_signature = "0"   # since we tamper with the message

    callback_data = CallbackData(**real_callback_data)

    # dummy handler will raise ValueError if nonce is "ERROR"
    callback_data.signedMessage = '{"classId":"1.x","objectId":"1.y","eventType":"save","expTimeMillis":1759331348143,"count":1,"nonce":"ERROR"}'

    from edutap.wallet_google.handlers.fastapi import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    resp = client.post(
        "/wallet/google/callback", json=callback_data.model_dump(mode="json")
    )
    assert resp.status_code == 500
    assert resp.text == '{"detail":"Error while handling the callbacks (exception)."}'


def test_callback_disabled_signature_check_NOTIMPLEMENTED(monkeypatch, mock_settings):
    from edutap.wallet_google.models.handlers import CallbackData

    # test callback handler without signature check
    mock_settings.handler_callback_verify_signature = "0"

    def raise_not_implemented():
        raise NotImplementedError

    # disable all plugins for callback_handlers - patch the instance at fastapi!
    monkeypatch.setattr(
        "edutap.wallet_google.handlers.fastapi.get_callback_handlers",
        raise_not_implemented,
    )

    callback_data = CallbackData(**real_callback_data)
    callback_data.signedMessage = '{"classId":"1.x","objectId":"1.y","eventType":"save","expTimeMillis":1734366082269,"count":1,"nonce":"abcde"}'

    from edutap.wallet_google.handlers.fastapi import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    resp = client.post(
        "/wallet/google/callback", json=callback_data.model_dump(mode="json")
    )
    assert resp.status_code == 500
    assert resp.text == '{"detail":"No callback handlers were registered."}'


def test_callback_disabled_signature_check_TIMEOUT(mock_settings):
    from edutap.wallet_google.models.handlers import CallbackData

    # test callback handler without signature check
    mock_settings.handler_callback_verify_signature = "0"
    # set low timeout to trigger a timeout cancellation
    mock_settings.handlers_callback_timeout = 0.1

    callback_data = CallbackData(**real_callback_data)
    callback_data.signedMessage = '{"classId":"TIMEOUT.x","objectId":"1.x","eventType":"save","expTimeMillis":250,"count":1,"nonce":"abcde"}'

    from edutap.wallet_google.handlers.fastapi import router

    class NeverEndingCallbackHandler:
        async def handle(
            self,
            class_id: str,
            object_id: str,
            event_type: str,
            exp_time_millis: int,
            count: int,
            nonce: str,
        ) -> None:
            import asyncio

            await asyncio.sleep(1000)

    add_plugin("CallbackHandler", NeverEndingCallbackHandler)

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    resp = client.post(
        "/wallet/google/callback", json=callback_data.model_dump(mode="json")
    )
    assert resp.status_code == 500
    assert resp.text == '{"detail":"Error while handling the callbacks (timeout)."}'

    remove_plugins(NeverEndingCallbackHandler)


def test_image_OK(mock_fernet_encryption_key, dummy_plugins):
    from edutap.wallet_google.handlers.fastapi import router
    from edutap.wallet_google.utils import encrypt_data

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    resp = client.get(f"/wallet/google/images/{encrypt_data('OK')}")
    assert resp.status_code == 200
    assert resp.text == "mock-a-jepg"


def test_image_ERROR(mock_fernet_encryption_key, dummy_plugins):
    from edutap.wallet_google.handlers.fastapi import router
    from edutap.wallet_google.utils import encrypt_data

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    resp = client.get(f"/wallet/google/images/{encrypt_data('ERROR')}")
    assert resp.status_code == 404
    assert resp.text == '{"detail":"Image not found."}'


def test_image_TIMEOUT(mock_settings, mock_fernet_encryption_key, dummy_plugins):
    mock_settings.handlers_image_timeout = 0.1

    from edutap.wallet_google.handlers.fastapi import router
    from edutap.wallet_google.utils import encrypt_data

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    resp = client.get(f"/wallet/google/images/{encrypt_data('TIMEOUT')}")
    assert resp.status_code == 500
    assert resp.text == '{"detail":"Error while handling the image (timeout)."}'


def test_image_CANCEL(mock_fernet_encryption_key, dummy_plugins):
    from edutap.wallet_google.handlers.fastapi import router
    from edutap.wallet_google.utils import encrypt_data

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    resp = client.get(f"/wallet/google/images/{encrypt_data('CANCEL')}")
    assert resp.status_code == 500
    assert resp.text == '{"detail":"Error while handling the image (cancel)."}'


def test_image_UNEXPECTED(mock_fernet_encryption_key, dummy_plugins):
    from edutap.wallet_google.handlers.fastapi import router
    from edutap.wallet_google.utils import encrypt_data

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    resp = client.get(f"/wallet/google/images/{encrypt_data('UNEXPECTED')}")
    assert resp.status_code == 500
    assert resp.text == '{"detail":"Error while handling the image (exception)."}'


def test_image_NOTIMPLEMENTED(monkeypatch, mock_fernet_encryption_key):
    from edutap.wallet_google.handlers.fastapi import router
    from edutap.wallet_google.utils import encrypt_data

    def raise_not_implemented():
        raise NotImplementedError

    # disable all plugins for callback_handlers - patch the instance at fastapi!
    monkeypatch.setattr(
        "edutap.wallet_google.handlers.fastapi.get_image_providers",
        raise_not_implemented,
    )

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    resp = client.get(f"/wallet/google/images/{encrypt_data('ANYWAY')}")
    assert resp.status_code == 500
    assert resp.text == '{"detail":"No image providers were registered."}'


def test_image_TO_MANY_REGISTERED(monkeypatch, mock_fernet_encryption_key):
    from edutap.wallet_google.handlers.fastapi import router
    from edutap.wallet_google.utils import encrypt_data

    # disable all plugins for callback_handlers - patch the instance at fastapi!
    monkeypatch.setattr(
        "edutap.wallet_google.handlers.fastapi.get_image_providers", lambda: [1, 2]
    )

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    resp = client.get(f"/wallet/google/images/{encrypt_data('ANYWAY')}")
    assert resp.status_code == 500
    assert resp.text == '{"detail":"Multiple image providers found, abort."}'
