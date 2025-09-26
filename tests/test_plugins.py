from edutap.wallet_google.models.handlers import ImageData

import pytest


def test_get_image_providers():
    from edutap.wallet_google.plugins import get_image_providers
    from edutap.wallet_google.protocols import ImageProvider

    plugins = get_image_providers()
    assert len(plugins) == 1
    assert isinstance(plugins[0], ImageProvider)


def test_get_callback_handlers():
    from edutap.wallet_google.plugins import get_callback_handlers
    from edutap.wallet_google.protocols import CallbackHandler

    plugins = get_callback_handlers()
    assert len(plugins) == 1
    assert isinstance(plugins[0], CallbackHandler)


def test_get_credentials_providers():
    from edutap.wallet_google.plugins import get_credentials_providers
    from edutap.wallet_google.protocols import CredentialsProvider

    plugins = get_credentials_providers()
    assert len(plugins) == 1
    assert isinstance(plugins[0], CredentialsProvider)


def test_get_callback_handlers_empty(monkeypatch):
    from edutap.wallet_google.plugins import get_callback_handlers

    monkeypatch.setattr(
        "edutap.wallet_google.plugins.entry_points",
        lambda *args, **kw: [],
    )
    with pytest.raises(NotImplementedError):
        get_callback_handlers()


def test_get_image_providers_empty(monkeypatch):
    from edutap.wallet_google.plugins import get_image_providers

    monkeypatch.setattr(
        "edutap.wallet_google.plugins.entry_points",
        lambda *args, **kw: [],
    )
    with pytest.raises(NotImplementedError):
        get_image_providers()


def test_get_callback_handlers_wrong_type(monkeypatch):
    from edutap.wallet_google.plugins import get_callback_handlers

    class MockEP:
        name = "CallbackHandler"

        def load(self):
            return self

    monkeypatch.setattr(
        "edutap.wallet_google.plugins.entry_points",
        lambda *args, **kw: [MockEP()],
    )
    with pytest.raises(ValueError):
        get_callback_handlers()


def test_get_image_providers_wrong_type(monkeypatch):
    from edutap.wallet_google.plugins import get_image_providers

    class MockEP:
        name = "ImageProvider"

        def load(self):
            return self

    monkeypatch.setattr(
        "edutap.wallet_google.plugins.entry_points",
        lambda *args, **kw: [MockEP()],
    )
    with pytest.raises(ValueError):
        get_image_providers()


class DummyImageProvider:
    async def image_by_id(self, image_id: str) -> ImageData:
        raise NotImplementedError


class DummyCallbackHandler:
    async def handle(
        self,
        class_id: str,
        object_id: str,
        event_type: str,
        exp_time_millis: int,
        count: int,
        nonce: str,
    ) -> None: ...


class DummyCredentialsProvider:
    def credentials_for_issuer(self, issuer_id: str) -> str:
        raise NotImplementedError


def test_add_plugin():
    """
    test adding plugins at runtime
    """
    from edutap.wallet_google.plugins import add_plugin
    from edutap.wallet_google.plugins import get_callback_handlers
    from edutap.wallet_google.plugins import get_credentials_providers
    from edutap.wallet_google.plugins import get_image_providers

    count_image_providers = len(get_image_providers())
    count_callback_handlers = len(get_callback_handlers())
    count_credentials_providers = len(get_credentials_providers())

    add_plugin("ImageProvider", DummyImageProvider)
    add_plugin("CallbackHandler", DummyCallbackHandler)
    add_plugin("CredentialsProvider", DummyCredentialsProvider)

    with pytest.raises(TypeError):
        add_plugin("CallbackHandler", DummyImageProvider)

    plugins = get_image_providers()
    assert len(plugins) == 1 + count_image_providers
    assert isinstance(plugins[-1], DummyImageProvider)

    plugins = get_callback_handlers()
    assert len(plugins) == 1 + count_callback_handlers
    assert isinstance(plugins[-1], DummyCallbackHandler)

    plugins = get_credentials_providers()
    assert len(plugins) == 1 + count_credentials_providers
    assert isinstance(plugins[-1], DummyCredentialsProvider)
