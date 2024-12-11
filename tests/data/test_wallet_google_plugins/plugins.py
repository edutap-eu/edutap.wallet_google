from typing import BinaryIO

import io


class TestImageProvider:
    """
    Implementation of edutap.wallet_google.protocols.ImageProvider
    """

    async def image_by_id(self, image_id: str) -> BinaryIO:
        return io.BytesIO()


class TestCallbackHandler:
    """
    Implementation of edutap.wallet_google.protocols.CallbackHandler
    """

    async def handle(self, pass_id: str) -> None: ...
