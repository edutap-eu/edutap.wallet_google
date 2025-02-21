from .protocols import CallbackHandler
from .protocols import ImageProvider
from importlib.metadata import entry_points

import typing


_POSSIBLE_PLUGINS = {
    "ImageProvider": ImageProvider,
    "CallbackHandler": CallbackHandler,
}

_PLUGIN_REGISTRY: dict[str, list[CallbackHandler | ImageProvider]] = {
    "ImageProvider": [],
    "CallbackHandler": [],
}


def add_plugin(name: str, klass: CallbackHandler | ImageProvider):
    if not isinstance(klass, _POSSIBLE_PLUGINS[name]):
        raise TypeError(f"{klass} not implements {name}")
    _PLUGIN_REGISTRY[name].append(klass)


def get_plugins(name: str) -> list[CallbackHandler | ImageProvider]:
    eps = entry_points(group="edutap.wallet_google.plugins")
    plugins = [ep.load() for ep in eps if ep.name.startswith(name)]
    plugins += _PLUGIN_REGISTRY.get(name, [])
    if not plugins:
        raise NotImplementedError("No image provider plug-in found")
    for plugin in plugins:
        if not isinstance(plugin, _POSSIBLE_PLUGINS[name]):
            raise ValueError(f"{plugin} not implements {name}")
    return [plugin() for plugin in plugins]


def get_image_providers() -> list[ImageProvider]:
    return typing.cast(list[ImageProvider], get_plugins("ImageProvider"))


def get_callback_handlers() -> list[CallbackHandler]:
    return typing.cast(list[CallbackHandler], get_plugins("CallbackHandler"))
