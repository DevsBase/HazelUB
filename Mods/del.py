from Hazel.enums import USABLE, WORKS
from pyrogram.client import Client
from pyrogram import filters
import pyrogram.types as types
from Hazel import Tele

@Tele.on_message(filters.command(['d','del','delete']), sudo=True)
async def delCommand(client: Client, m: types.Message):
    if (not m.reply_to_message):
       return await m.reply('Reply to a message.')
    try:
        await Tele.message(m).delete(business_connection_id=m.business_connection_id)
        await Tele.message(m.reply_to_message).delete(revoke=True, business_connection_id=m.business_connection_id)
    except: pass

MOD_CONFIG = {
    "name": "Delete",
    "help": "**Usage:**\n> .del (reply to a message) (Inline not supported)",
    "works": WORKS.ALL,
    "usable": USABLE.ALL
}