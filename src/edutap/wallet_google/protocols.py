from .models.handlers import ImageData
from typing import Protocol
from typing import runtime_checkable


@runtime_checkable
class ImageProvider(Protocol):

    async def image_by_id(self, image_id: str) -> ImageData:
        """
        :param image_id: Unique image identifier as string.
        :return: ImageData instance.

        :raises: LookupError if image_id was not found.
        """


@runtime_checkable
class CallbackHandler(Protocol):

    async def handle(
        self,
        class_id: str,
        object_id: str,
        event_type: str,
        exp_time_millis: int,
        count: int,
        nonce: str,
    ) -> None:
        """
        :param class_id: ClassId
        :param object_id: ObjectId
        :param event_type: EventType
        :param exp_time_millis: Expiration time in milliseconds
        :param count: count retries
        :param nonce: nonce UID

        :raises: ValueError
        """
