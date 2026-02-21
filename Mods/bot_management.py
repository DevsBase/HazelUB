from Hazel import Tele, SQLClient
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
import logging

logger = logging.getLogger("Mods.bot_management")

@Tele.bot.on_message(filters.command("login", prefixes=["/"]) & filters.private)
async def login_handler(c: Client, m: Message):
    # Owner Check
    if not Tele.mainClient or not Tele.mainClient.me:
        return await m.reply("Userbot is not fully started yet. Please wait.")
        
    owner_id = Tele.mainClient.me.id
    if m.from_user.id != owner_id:
        return await m.reply("Only the owner of the main userbot session can use this command.")

    if len(m.command) < 2:
        return await m.reply("Usage: /login session_string")

    session_string = m.text.split(None, 1)[1]
    
    # Show loading status
    status = await m.reply("Wait... trying to login with this session.")

    try:
        # 1. Save to Database
        success_db = await SQLClient.add_session(session_string)
        if not success_db:
            return await status.edit("This session is already in the database.")

        # 2. Dynamically Start Client
        success_start = await Tele.add_and_start_client(session_string)
        
        if success_start:
            await status.edit("✅ **Session Logged In Successfully!**\n\nThe new client is now active.")
        else:
            await status.edit("⚠️ **Session saved to DB, but failed to start now.**\n\nIt will be attempted again on next bot restart.")
            
    except Exception as e:
        logger.error(f"Error in /login handler: {e}")
        await status.edit(f"❌ **Error:** `{e}`")

@Tele.bot.on_message(filters.command("sessions", prefixes=["/"]) & filters.private)
async def sessions_handler(c: Client, m: Message):
    # Owner Check
    if not Tele.mainClient or not Tele.mainClient.me:
        return await m.reply("Userbot is not fully started yet.")
        
    owner_id = Tele.mainClient.me.id
    if m.from_user.id != owner_id:
        return await m.reply("Unauthorized.")

    txt = "**Active HazelUB Sessions:**\n\n"
    for i, client in enumerate(Tele._allClients):
        try:
            # me info might be cached
            me = client.me
            if not me: me = await client.get_me()
            txt += f"{i+1}. **{me.first_name}** (`{me.id}`)\n"
        except:
            txt += f"{i+1}. *[Unknown/Disconnected]*\n"
    
    await m.reply(txt)

MOD_NAME = "Bot Management"
MOD_HELP = "Management commands for the Telegram Bot.\n\nUsage (Private to Bot):\n> /login <session> - Add a new userbot session.\n> /sessions - List all active sessions."
