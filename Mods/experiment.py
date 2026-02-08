from Hazel import Tele, OneApi
from MultiSessionManagement.OneApi import OneApi as OneApiClass
import logging

logger = logging.getLogger(__name__)

@OneApi.on_hazel_client_update()
async def handle_hazel_client_update(client: OneApiClass, update: dict):
    logger.info(f"Hazel Client Update: {update}")