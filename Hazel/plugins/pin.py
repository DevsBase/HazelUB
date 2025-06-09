from .. import *
from pyrogram import *
import asyncio
from pyrogram.enums import *

@on_message(filters.command(["pin", "unpin"],prefixes=HANDLER)&filters.me)
async def pin_unpin(app, message):
  if not message.reply_to_message:
    return await message.reply("ℹ️ Please reply to a message to pin/unpin")
  chat = message.chat
  if chat.type != ChatType.PRIVATE:
    member = await app.get_chat_member(chat.id, message.from_user.id)
    if member.status == ChatMemberStatus.MEMBER or not member.privileges.can_pin_messages:
      return await message.reply("**You don't have enough admin rights to use this command ❌**")
  try:
    if message.command[0] == "pin": ser_msg = await message.reply_to_message.pin(True,True)
    else: ser_msg = await message.reply_to_message.unpin()
    try:
      await message.delete()
      await ser_msg.delete()
    except:pass
  except Exception as e:
    await message.reply(f"**Error:** `{e}`")

MOD_NAME = 'Pins'
MOD_HELP = ".pin <reply> - To pin the replied message!\n.unpin (reply) - To unpin the replied message!"