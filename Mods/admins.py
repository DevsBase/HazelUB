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
        return await m.reply("I need to be an admin to perform this action.")

    try:
        user = await Tele.get_user(c, m, chat_id, chat_member=True)
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

    if cmd in ["promote", "fpromote", "lpromote"]:
        
        if await Tele.is_admin(c, chat_id, user_id):
            return await m.reply(f"{mention} is already admin.")
        
        privs = ChatPrivileges(
            can_manage_chat=True,
            can_delete_messages=True,
            can_manage_video_chats=True,
            can_restrict_members=True,
            can_promote_members=(cmd == "fpromote"),
            can_change_info=(cmd != "lpromote"),
            can_invite_users=True,
            can_pin_messages=True,
        )
        try:
            await c.promote_chat_member(chat_id, user_id, privs)
            await c.set_administrator_title(chat_id, user_id, extra_arg)
            await m.reply(
                f"Promoted {mention}." if extra_arg else f"Promoted {mention} ({extra_arg})."
            )
        except Exception as e:
            await m.reply(f"Failed to promote: {e}")

    elif cmd == "demote":
        try:
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
        "> .promote (reply/id/mention/username) [title, __optional__] - Promote to admin\n"
        "> .fpromote (reply/id/mention/username) [title, __optional__] - Full promotion\n"
        "> .lpromote (reply/id/mention/username) [title, __optional__] - Low promotion\n"
        "> .demote (reply/id/mention/username) - Remove admin rights\n"
        "> .mute (reply/id/mention/username) - Mute a user\n"
        "> .tmute (reply/id/mention/username) [time, __optional__] - Timed mute (e.g., .tmute 1h, 1m, or 1d.)\n"
        "> .unmute (reply/id/mention/username) - Unmute user"
    ),
    "works": WORKS.GROUP,
    "usable": USABLE.OWNER & USABLE.SUDO
}