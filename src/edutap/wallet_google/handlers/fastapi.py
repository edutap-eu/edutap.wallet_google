from ..models.handlers import CallbackData
from ..plugins import get_callback_handlers
from ..plugins import get_image_providers
from ..session import session_manager
from ..utils import decrypt_data
from .validate import verified_signed_message
from fastapi import APIRouter
from fastapi import Request
from fastapi import Response
from fastapi.exceptions import HTTPException
from fastapi.logger import logger
from fastapi.responses import JSONResponse

import asyncio


# define routers for all use cases: callback, images, and the combined router (at bottom of file)
router_callback = APIRouter(
    prefix=session_manager.settings.handler_prefix_callback,
    tags=["edutap.wallet_google"],
)
router_images = APIRouter(
    prefix=session_manager.settings.handler_prefix_images,
    tags=["edutap.wallet_google"],
)


@router_callback.post("/callback")
async def handle_callback(request: Request, callback_data: CallbackData):
    """FastAPI handler for the callback endpoint.

    It is called by Google Wallet API when a user interacts with a pass.
    The callback is triggered on save and delete of a pass in the wallet.
    """
    # get the registered callback handlers
    try:
        handlers = get_callback_handlers()
    except NotImplementedError:
        raise HTTPException(
            status_code=500, detail="No callback handlers were registered."
        )

    # extract and verify message (given verification is not disabled)
    callback_message = verified_signed_message(callback_data)
    logger.debug(f"Got message {callback_message}")

    # call each handler asynchronously
    try:
        results: list = (
            # this could be replaced by async with asyncio.timeout(5.0) in Py 3.11
            # see also https://hynek.me/articles/waiting-in-asyncio/
            await asyncio.wait_for(
                asyncio.gather(
                    *(
                        handler.handle(
                            callback_message.classId,
                            callback_message.objectId,
                            callback_message.eventType.value,
                            callback_message.expTimeMillis,
                            callback_message.count,
                            callback_message.nonce,
                        )
                        for handler in handlers
                    ),
                    return_exceptions=True,
                ),
                timeout=session_manager.settings.handlers_callback_timeout,
            )
        )
    except asyncio.TimeoutError:
        logger.exception(
            f"Timeout after {session_manager.settings.handlers_callback_timeout}s while handling the callbacks.",
        )
        raise HTTPException(
            status_code=500, detail="Error while handling the callbacks (timeout)."
        )
    # results is a list of exceptions or None
    if any(results):
        logger.error("Error while handling a callbacks.")
        raise HTTPException(
            status_code=500, detail="Error while handling the callbacks (exception)."
        )
    return JSONResponse(content={"status": "success"})


@router_images.get("/images/{encrypted_image_id}")
async def handle_image(request: Request, encrypted_image_id: str):
    """FastAPI handler for the image endpoint.

    It is called by Google Wallet API to fetch images for a pass.
    """
    # get the registered image providers
    try:
        handlers = get_image_providers()
    except NotImplementedError:
        raise HTTPException(
            status_code=500, detail="No image providers were registered."
        )
    if len(handlers) > 1:
        logger.error("Multiple image providers found, abort.")
        raise HTTPException(
            status_code=500, detail="Multiple image providers found, abort."
        )

    handler = handlers[0]

    # decrypt the image id
    image_id = decrypt_data(encrypted_image_id)

    try:
        result = await asyncio.wait_for(
            handler.image_by_id(image_id),
            timeout=session_manager.settings.handlers_image_timeout,
        )
    except asyncio.TimeoutError:
        logger.exception(
            "Timeout Timeout after {session_manager.settings.handlers_image_timeout}s while handling the image.",
        )
        raise HTTPException(
            status_code=500, detail="Error while handling the image (timeout)."
        )
    except asyncio.CancelledError:
        logger.exception(
            "Cancelled while handling the image.",
        )
        raise HTTPException(
            status_code=500, detail="Error while handling the image (cancel)."
        )
    except LookupError:
        raise HTTPException(status_code=404, detail="Image not found.")
    except Exception:
        logger.exception(
            "Error while handling a image.",
        )
        raise HTTPException(
            status_code=500, detail="Error while handling the image (exception)."
        )
    return Response(
        content=result.data,
        media_type=result.mimetype,
        headers={"Cache-Control": session_manager.settings.handler_image_cache_control},
    )


# needs to be included after the routers are defined
router = APIRouter(
    prefix=session_manager.settings.handler_prefix,
)
router.include_router(router_callback)
router.include_router(router_images)
