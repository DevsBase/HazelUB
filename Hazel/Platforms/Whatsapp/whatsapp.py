from neonize.aioze.client import NewAClient
from neonize.aioze.events import MessageEv
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
        
        logger.info("Please scan the QR code below. It will expire in 20 sec.")
        asyncio.create_task(client.connect())
    
    async def stop(self):
        for client in self._allClients:
            try:
                await client.stop()
            except: pass
    
    def on_message(self):
        def decorator(func):
            for client in self._allClients:
                client.event(MessageEv)(func)
            return func
        return decorator
