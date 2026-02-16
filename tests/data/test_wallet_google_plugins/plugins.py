from edutap.wallet_google.models.handlers import ImageData

import asyncio


class TestImageProvider:
    """
    Implementation of edutap.wallet_google.protocols.ImageProvider
    """

    async def image_by_id(self, image_id: str) -> ImageData:
        # return some predictable data for unit testing
        if image_id == "OK":
            return ImageData(mimetype="image/jpeg", data=b"mock-a-jepg")
        if image_id == "ERROR":
            raise LookupError("Image not found.")
        if image_id == "CANCEL":
            raise asyncio.CancelledError("Cancelled")
        if image_id == "TIMEOUT":
            await asyncio.sleep(0.5)
        raise Exception("Unexpected image_id")


class TestCallbackHandler:
    """
    Implementation of edutap.wallet_google.protocols.CallbackHandler

    Used in tests to simulate a callback handler and possible errors.
    """

    async def handle(
        self,
        class_id: str,
        object_id: str,
        event_type: str,
        exp_time_millis: int,
        count: int,
        nonce: str,
    ) -> None:
        if class_id.startswith("TIMEOUT"):
            await asyncio.sleep(exp_time_millis / 1000)
        elif nonce:
            return
        raise ValueError("test case errors if nonce is 0")
