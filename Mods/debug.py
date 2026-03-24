
from neonize.aioze.events import MessageEv
from Hazel import WA
import logging

@WA.on_message()
async def wsf(client, event: MessageEv):
    logging.info("WA message received")

    msg = getattr(event, "message", None)

    if event.Message.conversation == ".hi":
        await client.reply_message("Hello", event)