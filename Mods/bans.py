from Hazel import Tele
from pyrogram import filters
from pyrogram.types import Message, User
from pyrogram.enums import MessageEntityType
from pyrogram.errors import PeerIdInvalid
import logging
from pyrogram.client import Client

logger = logging.getLogger(__name__)

@Tele.on_message(filters.command(["ban", 'unban', 'kick']) & filters.group, sudo=True)
async def banFunc(c: Client, m: Message): 
    ban_or_unban_or_kick = m.command[0]  # type: ignore

    if len(m.command) < 2 and not m.reply_to_message: # type: ignore
        return await m.reply(f"Provide a user to {ban_or_unban_or_kick}.")
    elif m.reply_to_message and m.reply_to_message.from_user.id == c.me.id: # type: ignore
        return await m.reply(f"You can't {ban_or_unban_or_kick} yourself.")
    
    if m.reply_to_message and hasattr(m.reply_to_message.from_user, 'id'):
        user = m.reply_to_message.from_user.id # type: ignore
    elif any(e.type == MessageEntityType.TEXT_MENTION for e in m.entities): # type: ignore
        for entity in m.entities: # type: ignore
            if entity.type != MessageEntityType.TEXT_MENTION:
                continue
            user = entity.user.id
            break
    else:
        user = (m.text.split(None, 1)[1]).replace('@', '') # type: ignore
    
    is_admin = await Tele.is_admin(c, m.chat.id) # type: ignore
    if not is_admin:
        return await m.reply("You must be admin to do this.")
    privileges = await Tele.get_chat_member_privileges(c, m.chat.id) # type: ignore
    if privileges and not privileges.can_restrict_members:
        return await m.reply("You are missing rights `can_restrict_members`.")
    
    try:
        if user and str(user).isdigit():
            user = int(user)
        user = await c.get_chat_member(m.chat.id, user_id=user) # type: ignore
        user = user.user
    except PeerIdInvalid:
        return await m.reply('PeerId is invalid. You must interacted with that person once, otherwise use thier username.')
    except Exception as e:
        logger.error(e)
        return await m.reply('User is not found.')
    
    if user.id == getattr(m.from_user, 'id'):
        return await m.reply(f"You can't {ban_or_unban_or_kick} yourself.")   
    elif ban_or_unban_or_kick == "ban":
        try:
            await c.ban_chat_member(m.chat.id, user.id) # type: ignore
            await m.reply(f"Banned {user.mention}.")
        except Exception as e:
            await m.reply(f"Failed to ban user {user.id}\n\n**Error:** {e}")
    elif ban_or_unban_or_kick == "unban":
        try:
            await c.unban_chat_member(m.chat.id, user.id) # type: ignore
            await m.reply(f"Unbanned {user.mention}.")
        except Exception as e:
            await m.reply(f"Failed to unban user {user.id}\n\n**Error:** {e}")
    elif ban_or_unban_or_kick == "kick":
        try:
            await c.ban_chat_member(m.chat.id, user.id) # type: ignore
            await c.unban_chat_member(m.chat.id, user.id) # type: ignore
            await m.reply(f"Kicked {user.mention}.")
        except Exception as e:
            await m.reply(f"Failed to kick user {user.id}\n\n**Error:** {e}")

MOD_NAME = "Admins"
MOD_HELP = "**Usage:**\n> .ban (reply/username/mention)\n> .unban (reply/username/mention)\n> .kick (reply/username/mention)"