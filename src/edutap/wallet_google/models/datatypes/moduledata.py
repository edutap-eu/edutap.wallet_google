from ..bases import Model
from .datetime import TimeInterval
from .general import Image
from .localized_string import LocalizedString


# Attribute order as in Google's documentation to make future updates easier!
# last check: 2025-01-22


class ModuleViewConstraints(Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/ValueAddedModuleData
    """

    displayInterval: TimeInterval | None = None


class ValueAddedModuleData(Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/ValueAddedModuleData
    """

    header: LocalizedString | None = None
    body: LocalizedString | None = None
    image: Image | None = None
    uri: str | None = None
    viewConstraints: ModuleViewConstraints | None = None
    sortIndex: int | None = None
