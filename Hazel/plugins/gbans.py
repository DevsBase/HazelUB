from .. import *
from pyrogram import *
from pyrogram import enums, errors
import asyncio
import time
import logging

log = logging.getLogger(__name__)

@on_message(filters.command(['gban', 'ungban'], prefixes=HANDLER) & filters.me)
async def gban_func(c, m) -> None:
  if m.reply_to_message:
    user_id = m.reply_to_message.from_user.id
  elif len(m.command) >= 2:
    user_id = str(m.command[1])
    try: user_id = (await c.get_users(user_id)).id
    except: return await m.reply('Cannot find them. make sure your id is correct!')
  else: return await m.reply("Okay, i'll gban. But who?")
  if user_id == c.me.id:
    return await m.reply("Nah. I won't do this on myself.")  
  a, p, t = m.command[0], await m.reply('Processing...'), time.time()
  success = 0
  async for dialog in c.get_dialogs():
    if dialog.chat.type in [enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]:
      chat = dialog.chat
      try:
        if a == "gban": await c.ban_chat_member(chat.id, user_id)
        else: await c.unban_chat_member(chat.id, user_id)
        success += 1
        await asyncio.sleep(2.1)
      except errors.FloodWait as e:
        return await m.reply(f"FloodwaitError: a wait of {e.value} is required.")
  await p.delete()
  await m.reply(f"""**✅ {'Gban' if a == 'gban' else 'Ungban'} Summary 🐬**

**🚫 Successfully {'banned' if a == 'gban' else 'unbanned'}:** __{success} chats__
**👤 User:** __{user_id}__
**🕒 Taken Time:** __{int(time.time() - t)}s__

**» 🦋 Join:** __@{Channel} & @{Support} ✨🥀__
    """)
    
MOD_NAME = "Gbans"
MOD_HELP = """.gban (reply|user_id) - Globally ban a user from all groups
.ungban (reply|user_id) - Globally unban a user from all groups
"""    