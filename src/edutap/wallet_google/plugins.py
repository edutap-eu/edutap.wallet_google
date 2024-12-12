from .protocols import CallbackHandler
from .protocols import ImageProvider
from importlib.metadata import entry_points
from typing import Iterable


def get_image_providers() -> Iterable[ImageProvider]:
    eps = entry_points(group="edutap.wallet_google.plugins")
    plugins = [ep.load() for ep in eps if ep.name == "ImageProvider"]
    for plugin in plugins:
        if not isinstance(plugin, ImageProvider):
            raise ValueError(f"{plugin} not implements ImageProvider")
    return [plugin() for plugin in plugins]


def get_callback_handlers() -> Iterable[CallbackHandler]:
    eps = entry_points(group="edutap.wallet_google.plugins")
    plugins = [ep.load() for ep in eps if ep.name == "CallbackHandler"]
    for plugin in plugins:
        if not isinstance(plugin, CallbackHandler):
            raise ValueError(f"{plugin} not implements CallbackHandler")
    return [plugin() for plugin in plugins]
