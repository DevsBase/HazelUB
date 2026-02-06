from pyrogram import Client, filters
from pyrogram.types import Message
from Hazel import Tele
import asyncio
import logging

logger = logging.getLogger("Hazel.Mods.purge")

@Tele.on_message(filters.command("purge") & filters.me & filters.group)
async def purgeFunc(app: Client, m: Message):
    if not m.reply_to_message:
        return await m.reply("Reply to the message you want to delete from.")
    start = m.reply_to_message.id
    end = m.id
    count = 0 
    await m.edit("...")
    for x in range(start, end + 1, 100):
        try:
            x = list(range(x, x+101))
            count += await app.delete_messages(m.chat.id, x)
            await asyncio.sleep(2.5)
        except Exception as e:
            logger.error(f"Error deleting messages {x}: {str(e)}")
    await m.edit(f'Deleted {count} messages.')