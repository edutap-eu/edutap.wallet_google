from ..models.callback import CallbackData
from ..plugins import get_callback_handlers
from ..session import session_manager
from .validate import verified_signed_message
from fastapi import APIRouter
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.logger import logger

import asyncio


router = APIRouter(
    prefix=session_manager.settings.callback_prefix,
    tags=["google_wallet"],
)


@router.post("/callback")
async def handle_callback(request: Request, callback_data: CallbackData):
    """FastAPI handler for the callback endpoint.

    It is called by Google Wallet API when a user interacts with a pass.
    The callback is triggered on save and delete of a pass in the wallet.
    """
    # get the registered callback handlers
    handlers = get_callback_handlers()
    if len(handlers) == 0:
        logger.warning("No callback handlers registered")
        raise HTTPException(
            status_code=500, detail="No callback handlers were registered."
        )

    # extract and verify message (given verification is not disabled)
    callback_message = verified_signed_message(callback_data)
    logger.debug(f"Got message {callback_message}")

    # call each handler asynchronously
    try:
        await asyncio.gather(
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
            )
        )
    except Exception:
        logger.exception("Error while handling a callback")
        raise HTTPException(
            status_code=500, detail="Error while handling the callback."
        )
    return {"status": "success"}
