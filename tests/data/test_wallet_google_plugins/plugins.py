from edutap.wallet_google.models.callback import CallbackData
from edutap.wallet_google.models.handlers import ImageData


class TestImageProvider:
    """
    Implementation of edutap.wallet_google.protocols.ImageProvider
    """

    async def image_by_id(self, image_id: str) -> ImageData:
        return ImageData(mimetype="image/jpeg", data=b"")


class TestCallbackHandler:
    """
    Implementation of edutap.wallet_google.protocols.CallbackHandler
    """

    async def handle(self, pass_id: CallbackData) -> None: ...
