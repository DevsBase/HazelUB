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
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time

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
    await m.edit(f"🚀 **Uptime:** `{uptime}`")

@Tele.on_message(filters.command("pong") & filters.me)
async def pong_cmd(c: Client, m: Message):
    await m.edit("**Pong!**")

# --- Inline Handlers ---

@Tele.bot.on_inline_query(filters.regex("^ping$"))
async def ping_inline(c: Client, q: InlineQuery):
    uptime = get_readable_time(int(time.time() - START_TIME))
    
    await q.answer([
        InlineQueryResultArticle(
            title="Ping",
            description="Check bot status.",
            input_message_content=InputTextMessageContent(
                f"**Pong!**\n"
                f"🕒 **Uptime:** `{uptime}`"
            )
        )
    ], cache_time=0)

MOD_NAME = "Ping"
MOD_HELP = "Check bot status.\n\nUsage:\n> .ping - Show Pong and Uptime via inline.\n> .uptime - Show uptime directly.\n> .pong - Simple reply."
