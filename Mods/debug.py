
from neonize.aioze.events import MessageEv
from Hazel import WA
import logging

@WA.on_message()
async def wsf(client, event: MessageEv):
    logging.info("WA message received")

    if event.Message.conversation == ".hi":
        
        await client.reply_message(f"Hello {event.Info.MessageSource.Sender}", event)