from pyrogram.client import Client
from pyrogram import filters
from Hazel import Tele

@Tele.on_message(filters.command(['d','del','delete']) & filters.me)
async def delCommand(client, m):
    if (not m.reply_to_message):
       return await m.reply('Reply to a message.')
    try:
        await m.delete()
        await m.reply_to_message.delete()
    except: pass