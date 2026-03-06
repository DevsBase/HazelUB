from Hazel.enums import USABLE, WORKS
from Hazel import Tele
from pyrogram import filters
from pyrogram.types import Message, User, ChatMember
from pyrogram.errors import PeerIdInvalid
import logging
from pyrogram.client import Client

logger = logging.getLogger(__name__)

@Tele.on_message(filters.command(["ban", 'unban', 'kick']) & filters.group, sudo=True)
async def banFunc(c: Client, m: Message):
    if not m.chat or not m.command or not m.from_user or not c.me:
        return
        
    chat_id = m.chat.id
    if chat_id is None:
        return

    me_id = c.me.id
    if me_id is None:
        return

    ban_or_unban_or_kick = m.command[0]
    
    if len(m.command) < 2 and not m.reply_to_message:
        return await m.reply(f"Provide a user to {ban_or_unban_or_kick}.")
    
    if m.reply_to_message and m.reply_to_message.from_user:
        if m.reply_to_message.from_user.id == me_id:
            return await m.reply(f"You can't {ban_or_unban_or_kick} yourself.")
    
    is_admin = await Tele.is_admin(c, chat_id)
    if not is_admin:
        return await m.reply("You must be admin to do this.")
        
    privileges = await Tele.get_chat_member_privileges(c, chat_id)
    if privileges and not privileges.can_restrict_members:
        return await m.reply("You are missing rights `can_restrict_members`.")
    
    try:
        _user = await Tele.get_user(c, message=m, chat_id=chat_id, chat_member=True) 
        if isinstance(_user, ChatMember) and _user.user:
            user: User = _user.user
        else:
            return await m.reply("User not found.")
    except PeerIdInvalid:
        return await m.reply("PeerId is invalid. You must interacted with that person once, otherwise use thier username.")
    except Exception as e:
        logger.error(e)
        return await m.reply("User is not found.")

    target_user_id = user.id
    if target_user_id is None:
        return
    
    if target_user_id == m.from_user.id:
        return await m.reply(f"You can't {ban_or_unban_or_kick} yourself.")   
        
    if ban_or_unban_or_kick == "ban":
        try:
            await c.ban_chat_member(chat_id, target_user_id)
            await m.reply(f"Banned {user.mention}.")
        except Exception as e:
            await m.reply(f"Failed to ban user {target_user_id}\n\n**Error:** {e}")
    elif ban_or_unban_or_kick == "unban":
        try:
            await c.unban_chat_member(chat_id, target_user_id)
            await m.reply(f"Unbanned {user.mention}.")
        except Exception as e:
            await m.reply(f"Failed to unban user {target_user_id}\n\n**Error:** {e}")
    elif ban_or_unban_or_kick == "kick":
        try:
            await c.ban_chat_member(chat_id, target_user_id)
            await c.unban_chat_member(chat_id, target_user_id)
            await m.reply(f"Kicked {user.mention}.")
        except Exception as e:
            await m.reply(f"Failed to kick user {target_user_id}\n\n**Error:** {e}")

MOD_CONFIG = {
    "name": "Bans",
    "help": "**Usage:**\n> .ban (reply/id/username/mention)\n> .unban (reply/username/mention)\n> .kick (reply/username/mention)\n\nOnly works on group.",
    "works": WORKS.GROUP,
    "usable": USABLE.OWNER & USABLE.SUDO
}