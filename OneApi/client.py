import websockets
import logging
import random
import json
from typing import Callable, NoReturn
from websockets.asyncio.client import ClientConnection

logger = logging.getLogger(__name__)

class Client:
    def __init__(self, url: str) -> None:
        if not url.endswith("/"):
            url += "/"
        self.url: str = url
        self.hazel_id: int = random.randint(10000, 99999)
        self.hazelClientConn: ClientConnection | None = None
        self._handlers = {}
        self._handlerTypes = ["hazelClient"]
    
    def registerHandler(self, type: str, handler: Callable) -> None:
        if type not in self._handlerTypes:
            raise ValueError(f"Invalid handler type: {type}. Valid types are: {self._handlerTypes}")
        self._handlers[type] = handler
    
    async def dispatchUpdate(self, type: str, update: dict) -> None:
        if type in self._handlers:
            for handler in self._handlers[type]:
                await handler(update)
        else:
            logger.warning(f"No handler registered for update type: {type}")

    async def connectHazelClient(self):
        try:
            self.hazelClientConn = await websockets.connect(self.url+f"ws/HazelUB?Hazel_ID={self.hazel_id}")
        except websockets.exceptions.InvalidURI as e:
            raise ConnectionError(f"Invalid OneApi URI: {e}")
        while True:
            update = await self.hazelClientConn.recv()
            try:
                update_dict = json.loads(update)
                await self.dispatchUpdate("hazelClient", update_dict)
            except json.JSONDecodeError:
                logger.error(f"Received invalid JSON update: {update}")
            except Exception as e:
                logger.error(e)
    

