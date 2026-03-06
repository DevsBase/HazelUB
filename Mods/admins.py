import asyncio
from datetime import datetime, timedelta
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message, ChatPrivileges, ChatPermissions, User, ChatMember
from pyrogram.errors import PeerIdInvalid
import logging

from Hazel.enums import USABLE, WORKS
from Hazel import Tele

logger = logging.getLogger(__name__)

def parse_time(time_str: str):
    unit = time_str[-1].lower()
    if unit not in ['m', 'h', 'd']:
        return None
    try:
        value = int(time_str[:-1])
        if unit == 'm': return timedelta(minutes=value)
        if unit == 'h': return timedelta(hours=value)
        if unit == 'd': return timedelta(days=value)
    except ValueError:
        return None

@Tele.on_message(filters.command(["mute", "tmute", "unmute", "promote", "fpromote", "lpromote", "demote"]) & filters.group, sudo=True)
async def admin_actions(c: Client, m: Message):
    if not m.chat or not m.command or not m.from_user or not c.me:
        return

    chat_id = m.chat.id
    if chat_id is None:
        return

    me_id = c.me.id
    if me_id is None:
        return

    cmd = m.command[0].lower()
    extra_arg = ""

    if reply := m.reply_to_message:
        if reply.from_user and len(m.command) > 1:
            extra_arg = m.command[1]
    elif not m.reply_to_message and len(m.command) > 2:
        extra_arg = m.command[2]
    
    is_admin = await Tele.is_admin(c, chat_id)
    if not is_admin:
        return await m.reply("You must be admin to do this.")

    try:
        user = await Tele.get_user(c, message=m, chat_id=chat_id, chat_member=True)
    except Exception:
        return await m.reply("User not found. Use a reply or mention.")

    if not user:
        return await m.reply("User not found.")

    if not isinstance(user, ChatMember):
        return
    
    user = user.user
    user_id = user.id
    mention = getattr(user, 'mention', user_id)
    
    if user_id == me_id:
        return await m.reply("I can't perform this action on myself.")
    my_privs = await Tele.get_chat_member_privileges(c, chat_id, me_id)
    if not my_privs:
        return await m.reply("cannot get my privilege")

    if cmd in ["promote", "fpromote", "lpromote"]:
        
        if await Tele.is_admin(c, chat_id, user_id):
            return await m.reply(f"{mention} is already admin.")
        if not my_privs.can_promote_members:
            return await m.reply("You are missing rights `can_promote_members`.")
        elif not my_privs.can_restrict_members:
            return await m.reply("You are missing rights `can_restrict_members`.")
        
        privs = ChatPrivileges(
            can_manage_chat = (my_privs.can_manage_chat),
            can_delete_messages = (cmd != "lpromote" and my_privs.can_delete_messages),
            can_manage_video_chats = (my_privs.can_manage_video_chats),
            can_restrict_members = (cmd != "lpromote" and my_privs.can_restrict_members),
            can_promote_members = (cmd == "fpromote"),
            can_change_info = (cmd != "lpromote" and my_privs.can_change_info),
            can_invite_users = (my_privs.can_invite_users),
            can_pin_messages = (cmd != "lpromote" and my_privs.can_pin_messages),
        )
        try:
            await c.promote_chat_member(chat_id, user_id, privs)
            await c.set_administrator_title(chat_id, user_id, extra_arg)
            await m.reply(
                f"Promoted {mention}." if extra_arg != '' else f"Promoted {mention} ({extra_arg})."
            )
        except Exception as e:
            await m.reply(f"Failed to promote: {e}")

    elif cmd == "demote":
        try:
            if not await Tele.is_admin(c, chat_id=chat_id, user_id=user_id):
                return await m.reply(f"{mention} is not admin already.")
            elif not my_privs.can_restrict_members:
                return await m.reply("You are missing rights `can_restrict_members`.")
            await c.promote_chat_member(
                chat_id, user_id, 
                ChatPrivileges(
                    can_manage_chat=False, 
                    can_delete_messages=False,
                    can_manage_video_chats=False,
                    can_restrict_members=False,
                    can_promote_members=False,
                    can_change_info=False,
                    can_invite_users=False,
                    can_pin_messages=False
                )
            )
            await m.reply(f"Demoted {mention}.")
        except Exception as e:
            await m.reply(f"Failed to demote: {e}")

    elif cmd in ["mute", "tmute"]:
        if not my_privs.can_restrict_members:
            return await m.reply("You are missing rights `can_restrict_members`.")
        until_date = datetime.now()
        if cmd == "tmute":
            if not extra_arg:
                return await m.reply("Usage: .tmute @user 1h` (m/h/d)")
            duration = parse_time(extra_arg)
            if not duration:
                return await m.reply("Invalid time format. Use 10m, 2h, or 7d.")
            until_date += duration
        else:
            until_date += timedelta(days=365) 

        try:
            await c.restrict_chat_member(
                chat_id, user_id,
                ChatPermissions(can_send_messages=False),
                until_date=until_date
            )
            time_str = extra_arg if cmd == "tmute" else "forever"
            await m.reply(f"Muted {mention} for {time_str}.")
        except Exception as e:
            await m.reply(f"Failed to mute: {e}")

    elif cmd == "unmute":
        if not my_privs.can_restrict_members:
            return await m.reply("You are missing rights `can_restrict_members`.")
        try:
            await c.restrict_chat_member(
                chat_id, user_id,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True
                )
            )
            await m.reply(f"Unmuted {mention}.")
        except Exception as e:
            await m.reply(f"Failed to unmute: {e}")

MOD_CONFIG = {
    "name": "Admins",
    "help": (
        "**Usage:**\n"
        "> .promote [$user$] [title, __optional__] - Promote to admin\n\n"
        "> .fpromote [$user$] [title, __optional__] - Full promotion\n\n"
        "> .lpromote [$user$] [title, __optional__] - Low promotion\n\n"
        "> .demote [$user$] - Remove admin rights\n\n"
        "> .mute [$user$] - Mute a user\n\n"
        "> .tmute [$user$]) [time] - Timed mute (e.g., .tmute 1h, 1m, or 1d.)\n\n"
        "> .unmute [$user$] - Unmute user"
    ),
    "works": WORKS.GROUP,
    "usable": USABLE.OWNER & USABLE.SUDO
}