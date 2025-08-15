from .. import *
from pyrogram import filters, raw
from datetime import datetime
from time import time

@on_message(filters.command("ping", prefixes=HANDLER) & filters.user('me'))
async def ping_pong(client, message):
  uptime = datetime.now() - start_time

  ping_start = time()
  await client.invoke(
    raw.functions.ping.Ping(ping_id=client.rnd_id())
  )
  ping_ms = round((time() - ping_start) * 1000.0, 3)

  await message.reply(
    f"» Pᴏɴɢ! Rᴇsᴘᴏɴsᴇ ᴛɪᴍᴇ: {ping_ms:.3f} ms\n"
    f"» Uᴘᴛɪᴍᴇ: {uptime.seconds // 3600}h {(uptime.seconds // 60) % 60}m {uptime.seconds % 60}s"
  )