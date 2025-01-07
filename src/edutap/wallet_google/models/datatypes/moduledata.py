from .datetime import TimeInterval
from .general import Image
from .localized_string import LocalizedString
from ..bases import Model


class ModuleViewConstraints(Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/ValueAddedModuleData
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-12-02
    displayInterval: TimeInterval | None = None


class ValueAddedModuleData(Model):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/ValueAddedModuleData
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-12-02
    header: LocalizedString | None = None
    body: LocalizedString | None = None
    image: Image | None = None
    uri: str | None = None
    viewConstraints: ModuleViewConstraints | None = None
    sortIndex: int | None = None
