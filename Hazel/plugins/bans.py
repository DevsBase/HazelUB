from .. import *
import logging
from pyrogram import *
from pyrogram.types import *
from pyrogram import enums
import asyncio

log = logging.getLogger(__name__)

async def is_admin(client, chat_id, user_id):
  member = await client.get_chat_member(chat_id, user_id)
  return member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]

@on_message(filters.command(["unbanall", "banall", "kickall"], prefixes=HANDLER) & filters.me)
async def gban_func(app,message)->None:
  user_id, chat_id = message.from_user.id, message.chat.id
  if not await is_admin(app, chat_id, user_id):
    return await message.reply('You should be an admin to do this.')
  if message.chat.type == enums.ChatType.PRIVATE:
    return await message.reply("This Command Only works in Groups!")
  if not (await app.get_chat_member(chat_id, app.me.id)).privileges.can_restrict_members:
    return await message.reply("I cannot. I don't have permission bro.")
  cmd = message.command[0]
  try:
    msg = await message.reply("Processing...")
    admins, members, count = [], [], 0
    async for m in app.get_chat_members(chat_id):
      if m.privileges: 
        admins.append(m.user.id)
      else: 
        members.append(m.user.id)
    if cmd == "unbanall":
      async for m in app.get_chat_members(chat_id, filter=enums.ChatMembersFilter.BANNED):
        try:
          await asyncio.sleep(1.5)
          await app.unban_chat_member(chat_id, m.user.id)
          count += 1
        except Exception as e:
          log.error(f"{app.me.first_name} ({app.me.id}): {e}")
      text = f"Found Banned Members: {count}\nUnbanned Successfully: {count}"
    else:
      for user_id in members:
        try:
          await asyncio.sleep(1.5)
          await app.ban_chat_member(chat_id, user_id)
          if cmd == "kickall":
            await app.unban_chat_member(chat_id, user_id)
          count += 1
        except Exception as e:
          log.error(f"{app.me.first_name} ({app.me.id}): {e}")
      action = "Kicked" if cmd == "kickall" else "Banned"
      text = f"Successfully {action}: {count}\nRemaining Admins: {len(admins)}"
    await message.reply(text)
    await msg.delete()
  except Exception as e:
    if "CHAT_ADMIN_REQUIRED" in str(e):
      return await message.reply("You cannot. Because you do not have enough privileges")
    await message.reply(f"**Error:** {e}")
    log.error(f"{app.me.first_name} ({app.me.id}): {e}")

@on_message(filters.command(['ban','kick','unban'],prefixes=HANDLER)&filters.me)
async def ban_func(c,m)->None:
  from MultiSessionManagement import clients
  if m.reply_to_message:
    victim = m.reply_to_message.from_user.id if not hasattr(m,'sender_chat') else m.reply_to_message.sender_chat.id
  elif len(m.command) >= 2:
    victim = str(m.command[1])
    try: victim = (await c.get_users(victim)).id
    except: return await m.reply('Cannot find them. make sure your id is correct!')
  else: return await m.reply(f"Okay, I'll {m.command[0]}. But who?")
  here = m.chat.id
  if (m.command[0] in ['ban','kick']):
    try:
      await c.ban_chat_member(here,victim)
      if (m.command[0] == 'kick'): await c.unban_chat_member(here,victim)
      return await m.reply("Banned." if m.command[0] == 'ban' else "Kicked.")
    except:
      if c.privilege == "sudo":
        for cl in clients:
          try:
            await cl.ban_chat_member(here,victim)
            if (m.command[0] == 'kick'): await cl.unban_chat_member(here,victim)
            return await m.reply("Banned." if m.command[0] == 'ban' else "Kicked.")
          except: pass
      return await m.reply("Failed.")
  else:
    try:
      await c.unban_chat_member(here,victim)
      return await m.reply("Unbanned.")
    except:
      if c.privilege == "sudo":
        for cl in clients:
          try:
            await cl.unban_chat_member(here,victim)
            return await m.reply("Unbanned.")
          except: pass
      return await m.reply("Failed.")

MOD_NAME = 'Bans'
MOD_HELP = """**⚕️ Banall**
.banall - To ban all members from a group.
.unbanall - To unban all members from a group.
.kickall - To kick all members from a group.

**🥀 Normal-Ban**
.ban <reply/id> - To ban them.
.kick <reply/id> - To kick them.
.unban <reply/id> - To unban them.
**💡 LMAO:** Don't try to test this and destroy your own group!"""