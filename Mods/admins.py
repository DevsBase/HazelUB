from Hazel import Tele
from pyrogram import Client, filters
from pyrogram.types import Message
import logging

logger = logging.getLogger(__name__)

@Tele.on_message(filters.command(["ban", 'unban', 'kick']) & filters.me & filters.group)
async def banFunc(c: Client, m: Message):
    ban_or_unban_or_kick = m.command[0]  # type: ignore
    if len(m.command) < 2 and not m.reply_to_message:
        return await m.reply(f"Provide a user to {ban_or_unban_or_kick}.")
    elif m.reply_to_message and m.reply_to_message.from_user.id == c.me.id: # type: ignore
        return await m.reply(f"You can't {ban_or_unban_or_kick} yourself.")
    
    if m.reply_to_message:
        user = m.reply_to_message.from_user.id # type: ignore
    else:
        user = (m.text.split(None, 1)[1]).replace('@', '')
    
    if str(user).isdigit() and int(user) == c.me.id: # type: ignore
        return await m.reply(f"You can't {ban_or_unban_or_kick} yourself.")
    elif str(user).lower() == (c.me.username).lower(): # type: ignore
        return await m.reply(f"You can't {ban_or_unban_or_kick} yourself.")

    is_admin = await Tele.is_admin(c, m.chat.id)
    if not is_admin:
        return await m.reply("You must be admin to do this.")
    privileges = await Tele.get_chat_member_privileges(c, m.chat.id)
    if privileges and not privileges.can_restrict_members:
        return await m.reply("You are missing rights `can_restrict_members`.")
    
    try:
        user = await c.get_chat_member(m.chat.id, user)
        user = user.user.id
    except Exception as e:
        logger.error(e)
        return await m.reply('User is not found.')
    
    if ban_or_unban_or_kick == "ban":
        try:
            await c.ban_chat_member(m.chat.id, user) # type: ignore
            await m.reply("Banned.")
        except Exception as e:
            await m.reply(f"Failed to ban user {user}\n\n**Error:** {e}")
    elif ban_or_unban_or_kick == "unban":
        try:
            await c.unban_chat_member(m.chat.id, user) # type: ignore
            await m.reply("Unbanned.")
        except Exception as e:
            await m.reply(f"Failed to unban user {user}\n\n**Error:** {e}")
    elif ban_or_unban_or_kick == "kick":
        try:
            await c.ban_chat_member(m.chat.id, user) # type: ignore
            await c.unban_chat_member(m.chat.id, user) # type: ignore
            await m.reply("Kicked.")
        except Exception as e:
            await m.reply(f"Failed to kick user {user}\n\n**Error:** {e}")