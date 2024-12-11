from typing import BinaryIO
from typing import Protocol
from typing import runtime_checkable


@runtime_checkable
class ImageProvider(Protocol):

    async def image_by_id(self, image_id: str) -> BinaryIO:
        """
        :param image_id: Unique image identifier as string.
        :return: BinaryIO containing image data.
        """


@runtime_checkable
class CallbackHandler(Protocol):

    async def handle(self, pass_id: str) -> None:
        """
        :param pass_id: Pass ID as string.
        """
