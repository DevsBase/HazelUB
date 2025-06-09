from pyrogram import filters
from .. import *
import asyncio
from pyrogram.enums import ChatType
import logging

@on_message(filters.command("purge", prefixes=HANDLER) & filters.me & filters.group)
async def purge_messages(app, message):
  if not message.reply_to_message:
    return await message.reply("Reply to the message you want to delete from.")
  await message.delete()
  start = message.reply_to_message.id
  end = message.id
  for x in range(start, end + 1, 100):
    try:
      x = list(range(x, x+101))
      await app.delete_messages(message.chat.id, x)
      await asyncio.sleep(2.5)
    except Exception as e:
      logging.error(f"Error deleting messages {x}: {str(e)}")
  
MOD_NAME = "Purge"
MOD_HELP = ".purge <reply> - To delete all messages from you replied one."