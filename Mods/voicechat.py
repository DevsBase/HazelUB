from Hazel import Tele
from pyrogram import Client, filters
from pyrogram.types import Message
import logging
import asyncio
import os

logger = logging.getLogger("Mods.voicechat")

@Tele.on_message(filters.command('play') & filters.me)
async def playFunc(c: Client, m: Message):
    query = " ".join(m.command[1:])
    try:
        path = await Tele.download_song(query, c)
        if not path:
            return await m.reply("Song not found.")
    except TimeoutError:
        return await m.reply("Timeout: DazzerBot doesn't give audio file")
    tgcalls = Tele.getClientPyTgCalls(c)
    if tgcalls:
        await tgcalls.play(m.chat.id, path)
        await asyncio.to_thread(os.remove, path)