from edutap.wallet_google.handlers.fastapi import router_callback
from edutap.wallet_google.models.handlers import ImageData
from fastapi import FastAPI


app = FastAPI()
app.include_router(router_callback)


class DisabledImageProvider:

    @property
    def active(self) -> bool:
        return False

    async def image_by_id(self, image_id: str) -> ImageData:
        """
        :param image_id: Unique image identifier as string.
        :return: ImageData instance.

        :raises: LookupError if image_id was not found.
        """
        raise LookupError()
