from ..models.callback import CallbackData
from .validate import verified_signed_message
from fastapi import Request
from fastapi import router
from fastapi.logger import logger


@router.post("/callback")
async def handle_callback(request: Request, callback_data: CallbackData):
    callback_message = verified_signed_message(callback_data)
    logger.debug(f"Got message {callback_message}")
    # TODO: here we need to call a plugin (async best) to handle the callback
    # and handle erross
    return {"status": "success"}
