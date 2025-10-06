"""Factory functions for creating Google Wallet model instances.

This module provides factory functions that are shared between sync and async APIs.
"""

from .registry import lookup_model_by_name
from .utils import validate_data

import typing


def new(
    name: str,
    data: dict[str, typing.Any] = {},
):
    """
    Factors a new registered Google Wallet Model by name, based on the given data.

    :param name:       Registered name of the model to use
    :param data:       Data to initialize the model with.
                       A simple JSON compatible Python data structure using built-ins.
    :raises Exception: When the data does not validate.
    :return:           The created model instance.
    """
    model = lookup_model_by_name(name)
    return validate_data(model, data)
