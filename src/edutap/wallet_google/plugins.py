from .protocols import CallbackHandler
from .protocols import ImageProvider
from importlib.metadata import entry_points


def get_image_providers() -> list[ImageProvider]:
    eps = entry_points(group="edutap.wallet_google.plugins")
    plugins = [ep.load() for ep in eps if ep.name.startswith("ImageProvider")]
    if not plugins:
        raise NotImplementedError("No image provider plug-in found")
    for plugin in plugins:
        if not isinstance(plugin, ImageProvider):
            raise ValueError(f"{plugin} not implements ImageProvider")
    return [plugin() for plugin in plugins]


def get_callback_handlers() -> list[CallbackHandler]:
    eps = entry_points(group="edutap.wallet_google.plugins")
    plugins = [ep.load() for ep in eps if ep.name.startswith("CallbackHandler")]
    if not plugins:
        raise NotImplementedError("No callback handler plugin found.")
    for plugin in plugins:
        if not isinstance(plugin, CallbackHandler):
            raise ValueError(f"{plugin} not implements CallbackHandler")
    return [plugin() for plugin in plugins]
