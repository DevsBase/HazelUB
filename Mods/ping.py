from Hazel import Tele, START_TIME, __version__
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
    bot_username = (await Tele.bot.get_me()).username
    results = await c.get_inline_bot_results(bot_username, "uptime")
    if results.results:
        await c.send_inline_bot_result(
            m.chat.id,
            results.query_id,
            results.results[0].id
        )
        await m.delete()

@Tele.on_message(filters.command("pong") & filters.me)
async def pong_cmd(c: Client, m: Message):
    start = datetime.now()
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await m.edit(f"**Pong!**\n`{ms}ms`")

# --- Inline Handlers ---

@Tele.bot.on_inline_query(filters.regex("^ping$"))
async def ping_inline(c: Client, q: InlineQuery):
    start = time.time()
    # We can't easily measure round trip here without a message, 
    # but we can show bot's internal latency/uptime.
    uptime = get_readable_time(int(time.time() - START_TIME))
    
    await q.answer([
        InlineQueryResultArticle(
            title="Ping",
            description="Check bot latency and uptime.",
            input_message_content=InputTextMessageContent(
                f"**HazelUB Stats**\n"
                f"![⚡](tg://emoji?id=5328303038660613219) **Latency:** `calculating...`\n"
                f"![🕒](tg://emoji?id=5328303038660613219) **Uptime:** `{uptime}`\n"
                f"![🤖](tg://emoji?id=5328303038660613219) **Version:** `{__version__}`"
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Refresh", callback_data="ping_refresh")]
            ])
        )
    ], cache_time=0)

@Tele.bot.on_inline_query(filters.regex("^uptime$"))
async def uptime_inline(c: Client, q: InlineQuery):
    uptime = get_readable_time(int(time.time() - START_TIME))
    await q.answer([
        InlineQueryResultArticle(
            title="Uptime",
            description=f"Bot has been running for {uptime}",
            input_message_content=InputTextMessageContent(
                f"![🚀](tg://emoji?id=5328303038660613219) **HazelUB Uptime:** `{uptime}`"
            )
        )
    ], cache_time=0)

@Tele.bot.on_callback_query(filters.regex("ping_refresh"))
async def ping_refresh_cb(c: Client, q):
    start = time.time()
    await q.answer("Refreshing...")
    end = time.time()
    ms = round((end - start) * 1000, 2)
    uptime = get_readable_time(int(time.time() - START_TIME))
    
    await q.edit_message_text(
        f"**HazelUB Stats**\n"
        f"![⚡](tg://emoji?id=5328303038660613219) **Latency:** `{ms}ms`\n"
        f"![🕒](tg://emoji?id=5328303038660613219) **Uptime:** `{uptime}`\n"
        f"![🤖](tg://emoji?id=5328303038660613219) **Version:** `{__version__}`",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Refresh", callback_data="ping_refresh")]
        ])
    )

MOD_NAME = "Ping"
MOD_HELP = "Check bot latency and uptime.\n\nUsage:\n> .ping - Stats with latency.\n> .uptime - Show uptime.\n> .pong - Simple reply."
