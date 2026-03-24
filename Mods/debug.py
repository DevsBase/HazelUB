
from neonize.aioze.events import MessageEv
from neonize.utils.jid import jid_is_lid
from Hazel import WA
import logging

@WA.on_message("test", from_me_only=True)
async def wsf(client, event: MessageEv):
    await client.reply_message(f"Hello thjere", event)