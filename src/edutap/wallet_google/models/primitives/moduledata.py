from . import Image
from .datetime import TimeInterval
from .localized_string import LocalizedString
from pydantic import BaseModel


class ModuleViewConstraints(BaseModel):
    """
    see: https://developers.google.com/wallet/reference/rest/v1/ValueAddedModuleData
    """

    # Attribute order as in Google's documentation to make future updates easier!
    # last check: 2024-12-02
    displayInterval: TimeInterval | None = None


class ValueAddedModuleData(BaseModel):
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
