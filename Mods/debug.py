# Hazel/Platforms/Whatsapp/handler.py

from neonize.aioze.events import ConnectedEv
from Hazel import WA
import logging

def setup():
    for c in WA._allClients:

        @c.event(ConnectedEv)
        async def wsf(client, event):
            logging.info("Client connected")

            msg = getattr(event, "message", None)
            chat = getattr(event, "chat", None)

            if msg and getattr(msg, "text", None):
                await client.send_message(chat_id=chat, text="yh")