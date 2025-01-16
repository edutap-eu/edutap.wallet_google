from edutap.wallet_google.handlers.fastapi import router_callback
from fastapi import FastAPI
from fastapi.logger import logger

import os
import pathlib


app = FastAPI()
app.include_router(router_callback)


class LoggingCallbackHandler:
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
    ) -> None:
        pathlib.Path(
            os.environ.get(
                "EDUTAP_WALLET_GOOGLE_EXAMPLE_CALLBACK_LOG_FILE", "./callback_log.txt"
            )
        )
        line = f'"{class_id}", "{object_id}", "{event_type}", "{exp_time_millis}", "{count}", "{nonce}"\n'
        logger.info(line)
        with open("callback_log.txt", "a") as file:
            file.write(line)
