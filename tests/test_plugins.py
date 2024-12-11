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
