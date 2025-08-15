from .. import *
from pyrogram import filters, raw
from datetime import datetime

@on_message(filters.command("ping", prefixes=HANDLER) & filters.user('me'))
async def ping_pong(client, message):
  uptime = datetime.now() - start_time

  ping_start = datetime.now()
  await client.invoke(
    raw.functions.ping.Ping(ping_id=client.rnd_id())
  )
  ping_ms = (datetime.now() - ping_start).total_seconds() * 1000

  await message.reply(
    f"» Pᴏɴɢ! Rᴇsᴘᴏɴsᴇ ᴛɪᴍᴇ: {ping_ms:.3f} ms\n"
    f"» Uᴘᴛɪᴍᴇ: {uptime.seconds // 3600}h {(uptime.seconds // 60) % 60}m {uptime.seconds % 60}s"
  )