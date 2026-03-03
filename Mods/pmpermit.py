from Hazel.enums import USABLE, WORKS
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
from Hazel import Tele, SQLClient
from MultiSessionManagement.decorators import _sudo_check
from typing import Dict

# Rate limiting / warning cache
# Format: {client_id: {user_id: warning_count}}
pm_warns: Dict[int, Dict[int, int]] = {}

DEFAULT_PM_MESSAGE = (
    "**⚠️ PMPermit Active ⚠️**\n\n"
    "I am currently not accepting private messages from unapproved users.\n"
    "Please wait for my approval to send messages here.\n"
    "You have {warns}/{limit} warnings left before being blocked."
)

@Tele.on_message(filters.command(["pmpermit"]) & filters.me)
async def pmpermit_cmd(c: Client, m: Message):
    """Toggle PMPermit on or off."""
    if not c.me or not c.me.id or not SQLClient:
        return
    if getattr(c.me, "is_bot", False):
        return
    if m.from_user and m.from_user.id != c.me.id:
        return
        
    if not m.command or len(m.command) < 2:
        await m.reply("**Usage:** `.pmpermit on|off`")
        return
        
    state = m.command[1].lower()
    if state == "on":
        await SQLClient.set_pmpermit(c.me.id, True)
        await m.reply("**PMPermit has been ENABLED**")
    elif state == "off":
        await SQLClient.set_pmpermit(c.me.id, False)
        await m.reply("**PMPermit has been DISABLED**")
    else:
        await m.reply("**Usage:** `.pmpermit on|off`")


@Tele.on_message(filters.command(["approve", "a"]) & filters.me)
async def approve_cmd(c: Client, m: Message):
    """Approve a user for PM."""
    if not c.me or not c.me.id or not SQLClient:
        return
    if getattr(c.me, "is_bot", False):
        return
    if m.from_user and m.from_user.id != c.me.id:
        return
        
    user = await Tele.get_user(c, m)
    if not user:
        await m.reply("**Please reply to a user or provide their ID/username.**")
        return
        
    user_id = getattr(user, "id", None)
    if not user_id:
        return
        
    await SQLClient.approve_user(c.me.id, user_id)
    
    # Reset warning cache for this user if it exists
    if c.me.id in pm_warns and user_id in pm_warns[c.me.id]:
        del pm_warns[c.me.id][user_id]
        
    first_name = getattr(user, "first_name", str(user_id))
    await m.reply(f"**{first_name}** has been approved to PM.")

@Tele.on_message(filters.command(["disapprove", "da"]) & filters.me)
async def disapprove_cmd(c: Client, m: Message):
    """Disapprove a user from PM."""
    if not c.me or not c.me.id or not SQLClient:
        return
    if getattr(c.me, "is_bot", False):
        return
    if m.from_user and m.from_user.id != c.me.id:
        return

    user = await Tele.get_user(c, m)
    if not user:
        await m.reply("**Please reply to a user or provide their ID/username.**")
        return
        
    user_id = getattr(user, "id", None)
    if not user_id:
        return
        
    await SQLClient.disapprove_user(c.me.id, user_id)
    
    first_name = getattr(user, "first_name", str(user_id))
    await m.reply(f"**{first_name}** has been disapproved from PM.")

@Tele.on_message(filters.command(["setpmmsg"]) & filters.me)
async def setpmmsg_cmd(c: Client, m: Message):
    """Set custom PMPermit warning message."""
    if not c.me or not c.me.id or not SQLClient:
        return
    if getattr(c.me, "is_bot", False):
        return
    if m.from_user and m.from_user.id != c.me.id:
        return
        
    if not m.command or len(m.command) < 2 or not m.text:
        await m.reply("**Usage:** `.setpmmsg <text>`\nUse `{warns}` and `{limit}` as placeholders.")
        return
        
    msg = m.text.split(None, 1)[1]
    await SQLClient.set_pmpermit_message(c.me.id, msg)
    await m.reply("**Custom PMPermit message updated successfully.**")

@Tele.on_message(filters.command(["pmlimit"]) & filters.me)
async def pmlimit_cmd(c: Client, m: Message):
    """Set PMPermit warning limit."""
    if not c.me or not c.me.id or not SQLClient:
        return
    if getattr(c.me, "is_bot", False):
        return
    if m.from_user and m.from_user.id != c.me.id:
        return
        
    if not m.command or len(m.command) < 2 or not m.command[1].isdigit():
        await m.reply("**Usage:** `.pmlimit <number>`")
        return
        
    limit = int(m.command[1])
    if limit < 1:
        await m.reply("**Limit must be greater than 0.**")
        return
        
    await SQLClient.set_pmpermit_limit(c.me.id, limit)
    await m.reply(f"**PMPermit warning limit set to {limit}.**")


@Tele.on_message(filters.private & filters.incoming & ~filters.me & ~filters.bot, group=3)
async def pmpermit_handler(c: Client, m: Message):
    """Handle incoming private messages for PMPermit."""
    if not c.me or not c.me.id or not SQLClient:
        return
    
    if not m.from_user:
        return
        
    # Check if PMPermit is enabled
    is_enabled = await SQLClient.is_pmpermit_enabled(c.me.id)
    if not is_enabled:
        return

    # Skip checks if Sudoer
    if await _sudo_check(None, c, m):
        return
        
    # Check if approved
    if await SQLClient.is_approved(c.me.id, m.from_user.id):
        return

    client_id = c.me.id
    user_id = m.from_user.id
    
    # Initialize warning counts
    if client_id not in pm_warns:
        pm_warns[client_id] = {}
        
    warns = pm_warns[client_id].get(user_id, 0) + 1
    
    limit = await SQLClient.get_pmpermit_limit(c.me.id)
    
    if warns > limit:
        if user_id in pm_warns[client_id]:
            del pm_warns[client_id][user_id]
        await m.reply("**You have exceeded the warning limit and have been blocked.**")
        await c.block_user(user_id)
        return
    else:
        pm_warns[client_id][user_id] = warns
        
    # Fetch custom message or use default
    custom_msg = await SQLClient.get_pmpermit_message(c.me.id)
    warn_text = custom_msg if custom_msg else DEFAULT_PM_MESSAGE
    
    warn_text = warn_text.replace("{warns}", str(warns)).replace("{limit}", str(limit))
    await m.reply(warn_text)

MOD_NAME = "PMPermit"
MOD_HELP = (
    "> .pmpermit on|off - Toggle PMPermit.\n"
    "> .approve / .a (reply/id) - Approve a user.\n"
    "> .disapprove / .da (reply/id) - Disapprove a user.\n"
    "> .setpmmsg <text> - Set custom warning message.\n"
    "> .pmlimit <int> - Set warning limit."
    "\nNote: Sudoers are exempt from PMPermit checks. Use `.sudoers` to manage sudo users."
)

MOD_WORKS = WORKS.PRIVATE
MOD_USABLE = USABLE.OWNER