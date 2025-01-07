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
