from Hazel import Tele, SQLClient
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.client import Client
import logging

logger = logging.getLogger("Mods.Sudo")

# Helper to get user ID from command
async def get_user_id(c: Client, m: Message) -> tuple:
    if m.reply_to_message:
        return m.reply_to_message.from_user.id, m.reply_to_message.from_user.first_name
    
    if len(m.command) < 2:
        return None, None
    
    user_input = m.command[1]
    try:
        if user_input.isdigit():
            user_id = int(user_input)
            user = await c.get_users(user_id)
            return user.id, user.first_name
        else:
            user = await c.get_users(user_input.replace("@", ""))
            return user.id, user.first_name
    except Exception as e:
        logger.error(f"Failed to get user: {e}")
        return None, None

@Tele.on_message(filters.command("sudo") & filters.me)
async def sudo_add(c: Client, m: Message):
    user_id, name = await get_user_id(c, m)
    if not user_id:
        return await m.edit("❌ **Usage:** `.sudo <id/username>` or reply to a message.")
    
    await SQLClient.add_sudo(user_id, "sudo")
    await m.edit(f"✅ **{name}** (`{user_id}`) has been added as **Sudo**.")

@Tele.on_message(filters.command("fsudo") & filters.me)
async def fsudo_add(c: Client, m: Message):
    user_id, name = await get_user_id(c, m)
    if not user_id:
        return await m.edit("❌ **Usage:** `.fsudo <id/username>` or reply to a message.")
    
    await SQLClient.add_sudo(user_id, "fsudo")
    await m.edit(f"✅ **{name}** (`{user_id}`) has been added as **FSudo** (Full Sudo).")

@Tele.on_message(filters.command(["rmvsudo", "unfsudo"]) & filters.me)
async def sudo_rm(c: Client, m: Message):
    user_id, name = await get_user_id(c, m)
    if not user_id:
        return await m.edit("❌ **Usage:** `.rmvsudo <id/username>` or reply to a message.")
    
    await SQLClient.remove_sudo(user_id)
    await m.edit(f"🗑️ Authorized access removed for **{name}** (`{user_id}`).")

@Tele.on_message(filters.command("sudolist") & filters.me)
async def sudo_list(c: Client, m: Message):
    all_users = await SQLClient.get_all_sudo()
    if not all_users:
        return await m.edit("⚠️ No sudo users found.")
    
    text = "**Authorized Sudo Users:**\n\n"
    for u in all_users:
        level = "**FSudo**" if u["level"] == "fsudo" else "Sudo"
        text += f"• `{u['user_id']}` - {level}\n"
    
    await m.edit(text)

@Tele.on_message(filters.command("reloadsudo") & filters.me)
async def sudo_reload(c: Client, m: Message):
    await SQLClient.reload_sudo_cache()
    await m.edit("✅ Sudo cache reloaded successfully.")

MOD_NAME = "Auth"
MOD_HELP = "Manage authorized sudo users.\n\nUsage:\n> .sudo (reply/user) - Restricted sudo\n> .fsudo (reply/user) - Full sudo\n> .rmvsudo (reply/user) - Remove access\n> .sudolist - List all\n> .reloadsudo - Refresh cache"
