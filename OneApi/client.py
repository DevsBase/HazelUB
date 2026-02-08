import json
import logging
import inspect
from typing import Callable, Dict, List

import websockets
from websockets.asyncio.client import ClientConnection

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, url: str) -> None:
        if not url.endswith("/"):
            url += "/"

        self.url: str = url
        self.hazel_id: int = 0
        self.hazelClientConn: ClientConnection | None = None

        # event_type -> list of handlers
        self._handlers: Dict[str, List[Callable]] = {}
        self._handlerTypes = {"hazelClient"}

    # -----------------------------
    # Handler registration
    # -----------------------------
    def registerHandler(self, event: str, handler: Callable) -> None:
        if event not in self._handlerTypes:
            raise ValueError(
                f"Invalid handler type: {event}. Valid types: {self._handlerTypes}"
            )

        self._handlers.setdefault(event, []).append(handler)

    # Decorator System
    def on_update(self, event: str):
        def decorator(func: Callable):
            self.registerHandler(event, func)
            return func
        return decorator

    # -----------------------------
    # Dispatch system
    # -----------------------------
    async def dispatchUpdate(self, event: str, update: dict) -> None:
        handlers = self._handlers.get(event)

        if not handlers:
            logger.warning(f"No handler registered for update type: {event}")
            return

        for handler in handlers:
            try:
                if inspect.iscoroutinefunction(handler):
                    await handler(self, update)
                else:
                    handler(self, update)
            except Exception as e:
                logger.error(f"Handler error [{event}]: {e}")

    # -----------------------------
    # WebSocket connection
    # -----------------------------
    async def connectHazelClient(self, hazel_id: int) -> None:
        self.hazel_id = hazel_id
        logger.info(
            f"Connecting to OneApi..."
        )
        if not self.hazelClientConn is None:
            logger.warning("Already connected to OneApi, skipping connection.")
            return
        try:
            self.hazelClientConn = await websockets.connect(
                self.url + f"ws/HazelUB?Hazel_ID={self.hazel_id}"
            )
        except websockets.exceptions.InvalidURI as e:
            raise ConnectionError(f"Invalid OneApi URI: {e}")

        assert self.hazelClientConn is not None
        logger.info(
            f"Connected to OneApi successfully. Please Connect Your HazelUB Client in using {self.hazel_id} to use our ecosystem!"
        )
        while True:
            try:
                message = await self.hazelClientConn.recv()
                data = json.loads(message)
                
                if data.get("type") == 'client_joined':
                    logger.info(f"Hazel Client connected.")
                elif data.get("type") == 'client_left':
                    logger.info(f"Hazel Client disconnected.")

                await self.dispatchUpdate("hazelClient", data)

            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received: {message}")

            except websockets.exceptions.ConnectionClosed:
                logger.error("WebSocket connection closed, Restart HazelUB to reconnect.")
                break

            except Exception as e:
                logger.error(f"WebSocket loop error: {e}")
