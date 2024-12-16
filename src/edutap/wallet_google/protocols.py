from .models.callback import SignedMessage
from .models.handlers import ImageData
from typing import Protocol
from typing import runtime_checkable


@runtime_checkable
class ImageProvider(Protocol):

    async def image_by_id(self, image_id: str) -> ImageData:
        """
        :param image_id: Unique image identifier as string.
        :return: ImageData instance.
        """


@runtime_checkable
class CallbackHandler(Protocol):

    async def handle(self, message: SignedMessage) -> None:
        """
        :param pass_id: Pass ID as string.
        """
