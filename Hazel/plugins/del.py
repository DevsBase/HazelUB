from .. import *
from pyrogram import *

@on_message(filters.command(['d','del','delete'], prefixes=HANDLER) & filters.me)
async def d(_,m):
  if (not m.reply_to_message): return await m.reply('Reply to a message.')
  try: await m.delete(), await m.reply_to_message.delete()
  except: pass