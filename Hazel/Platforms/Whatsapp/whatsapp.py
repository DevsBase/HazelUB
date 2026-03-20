from neonize.aioze.client import NewAClient
from typing import List
import logging
import asyncio

logger = logging.getLogger("Platforms.WhatsApp")

class WhatsApp:
    def __init__(self) -> None:
        self._allClients: List[NewAClient] = []
    
    def create_neonize_client(self, name: str, *args, **kwargs) -> NewAClient:
        client = NewAClient(name, *args, **kwargs)
        self._allClients.append(client)
        return client

    async def connect_neonize_client(self, client: NewAClient):
        if not isinstance(client, NewAClient):
            raise ValueError("Arg. client must be neonize.client.NewAClient")
        if client not in self._allClients:
            raise ValueError("Client is must be create with `create_neonize_client` method.")
        if client.is_logged_in:
            raise Exception("The client is already logged in.")
        logger.info("Please scan the QR code below. It will expire in 20 sec.")
        asyncio.create_task(client.connect())
