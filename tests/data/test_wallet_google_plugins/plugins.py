from edutap.wallet_google.models.handlers import ImageData


class TestImageProvider:
    """
    Implementation of edutap.wallet_google.protocols.ImageProvider
    """

    async def image_by_id(self, image_id: str) -> ImageData:
        return ImageData(mimetype="image/jpeg", data=b"mock-a-jepg")


class TestCallbackHandler:
    """
    Implementation of edutap.wallet_google.protocols.CallbackHandler
    """

    async def handle(
        self,
        class_id: str,
        object_id: str,
        event_type: str,
        exp_time_millis: int,
        count: int,
        nonce: str,
    ) -> None: ...
