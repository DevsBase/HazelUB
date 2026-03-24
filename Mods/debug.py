
from neonize.aioze.events import MessageEv
from neonize.utils.jid import jid_is_lid
from Hazel import WA
import logging

@WA.on_message()
async def wsf(client, event: MessageEv):
    logging.info("WA message received")

    if event.Message.conversation == ".hi":
        sender = event.Info.MessageSource.Sender
        if jid_is_lid(sender):
            sender_alt = event.Info.MessageSource.SenderAlt
            sender = sender_alt if sender_alt.User else sender
            phone_number = sender.User
        await client.reply_message(f"Hello {phone_number}", event)