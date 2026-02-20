from pyrogram.client import Client
from pyrogram import filters
import pyrogram.types as types
from Hazel import Tele

@Tele.on_message(filters.command(['d','del','delete']) & filters.me)
async def delCommand(client: Client, m: types.Message):
    if (not m.reply_to_message):
       return await m.reply('Reply to a message.')
    try:
        await m.delete()
        await m.reply_to_message.delete(revoke=True)
    except: pass

MOD_NAME = "Delete"
MOD_HELP = "**Usage:**\n> .del (reply to a message)"
