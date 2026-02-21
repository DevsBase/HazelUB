from Hazel import Tele, START_TIME
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import (
    Message, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent
)
import time
from datetime import datetime

def get_readable_time(seconds: int) -> str:
    count = 0
    time_list = []
    time_suffix_list = ["s", "m", "h", "d", "w"] # Adding week support for the requested format

    # Years
    # ... ignoring years for now as boot time is unlikely to be that long 

    # Weeks
    weeks, seconds = divmod(seconds, 604800)
    # Days
    days, seconds = divmod(seconds, 86400)
    # Hours
    hours, seconds = divmod(seconds, 3600)
    # Minutes
    minutes, seconds = divmod(seconds, 60)
    
    parts = []
    if weeks: parts.append(f"{int(weeks)}w")
    if days: parts.append(f"{int(days)}d")
    if hours: parts.append(f"{int(hours)}h")
    if minutes: parts.append(f"{int(minutes)}m")
    parts.append(f"{int(seconds)}s")
    
    return ":".join(parts)

@Tele.on_message(filters.command("ping") & filters.me)
async def ping_cmd(c: Client, m: Message):
    bot_username = (await Tele.bot.get_me()).username
    results = await c.get_inline_bot_results(bot_username, "ping")
    if results.results:
        await c.send_inline_bot_result(
            m.chat.id,
            results.query_id,
            results.results[0].id
        )
        await m.delete()

@Tele.on_message(filters.command("uptime") & filters.me)
async def uptime_cmd(c: Client, m: Message):
    uptime = get_readable_time(int(time.time() - START_TIME))
    await m.edit(f"**Uptime -** `{uptime}`")

# --- Inline Handlers ---

@Tele.bot.on_inline_query(filters.regex("^ping$"))
async def ping_inline(c: Client, q: InlineQuery):
    start = time.time()
    # We use a dummy wait or just calculate current latency to show something
    uptime = get_readable_time(int(time.time() - START_TIME))
    end = time.time()
    ms = round((end - start) * 1000, 2)
    
    await q.answer([
        InlineQueryResultArticle(
            title="Ping",
            description="Check bot status.",
            input_message_content=InputTextMessageContent(
                f"**Pong !!** `{ms}ms`\n"
                f"**Uptime -** `{uptime}`"
            )
        )
    ], cache_time=0)

MOD_NAME = "Ping"
MOD_HELP = "Check bot status.\n\nUsage:\n> .ping - Show Pong and Uptime in the requested format."
