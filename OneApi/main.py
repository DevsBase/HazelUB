import logging
from .client import Client

logger = logging.getLogger("OneApi")

async def main(url: str):
    OneClient = Client(url)
    await OneClient.connectHazelClient()
    return OneClient
