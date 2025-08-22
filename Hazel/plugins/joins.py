from .. import *
from pyrogram import *
from pyrogram.errors import InviteRequestSent

@on_message(filters.command(['join','leave'], prefixes=HANDLER) & filters.me)
async def joins_func(app,m):
  if (len(m.command) < 2 and m.command[0]=='leave' and m.chat.type not in [enums.ChatType.BOT,enums.ChatType.PRIVATE]):
    if '-silent' in m.text:
      await m.delete()
    else: await m.reply(f"Left from {m.chat.title}.")    
    await app.leave_chat(m.chat.id)
  elif (len(m.command) < 2):
    return await m.reply(f'need username/link to {m.command[0]}.')
  
  link = m.text.split(" ")[1]
  if m.command[0]=='join':
    try:
      chat = await app.join_chat(link)
      await m.reply(f"Joined, {chat.title}")
    except InviteRequestSent:
      return await m.reply("Join request sent.")
    except Exception as e: return await m.reply(f'Failed: {e}')
  else:
    try:
      chat = await app.leave_chat(link)  
      await m.reply(f'Left from {chat.title}.')      
    except Exception as e: return await m.reply(f'Failed: {e}')
      
MOD_NAME = "joins"
MOD_HELP = ".join <link/username> - to join there\n.leave <link/username/blank> - pass chat link or use in a group to leave from there."