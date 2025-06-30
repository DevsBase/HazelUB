from .. import *
from pyrogram import filters
import requests
from datetime import datetime

@on_message(filters.command("ping", prefixes=HANDLER) & filters.user('me'))
async def ping_pong(client, message):
  uptime = datetime.now() - start_time
  await message.reply_text(f"» Pᴏɴɢ! Rᴇsᴘᴏɴsᴇ ᴛɪᴍᴇ: {await app.ping()} ms\n» Uᴘᴛɪᴍᴇ: {uptime.seconds // 3600}h {(uptime.seconds // 60) % 60}m {uptime.seconds % 60}s")