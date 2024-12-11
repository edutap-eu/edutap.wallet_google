from .protocols import CallbackHandler
from .protocols import ImageProvider
from importlib.metadata import entry_points
from typing import Iterable


def get_image_providers() -> Iterable[ImageProvider]:
    eps = entry_points(group="edutap.wallet_google.plugins")
    return [ep.load() for ep in eps if ep.name == "ImageProvider"]


def get_callback_handlers() -> Iterable[CallbackHandler]:
    eps = entry_points(group="edutap.wallet_google.plugins")
    return [ep.load() for ep in eps if ep.name == "CallbackHandler"]
