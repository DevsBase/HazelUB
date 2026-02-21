from Hazel import Tele, START_TIME
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import (
    Message,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent
)
import time
import logging

logger = logging.getLogger("Hazel.Ping")

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

    for i in range(len(time_list)):
        time_list[i] = str(time_list[i]) + time_suffix_list[i]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time

@Tele.on_message(filters.command("ping"), sudo=True)
async def ping_cmd(c: Client, m: Message):
    start = time.time()
    bot_me = await Tele.bot.get_me()
    bot_username = bot_me.username
    
    # Calculate latency
    end = time.time()
    latency = int((end - start) * 1000)
    uptime = get_readable_time(int(time.time() - START_TIME))
    
    try:
        results = await c.get_inline_bot_results(bot_username, f"ping {latency} {uptime}")
        if results.results:
            await c.send_inline_bot_result(
                m.chat.id,
                results.query_id,
                results.results[0].id
            )
            if m.from_user and m.from_user.id == c.me.id:
                try: await m.delete()
                except: pass
        else:
            raise ValueError("No results")
    except Exception as e:
        logger.error(f"Inline ping failed: {e}")
        await m.reply(
            f"**Pong !!**\n"
            f"**Latency -** `{latency}ms`\n"
            f"**Uptime -** `{uptime}`"
        )

@Tele.on_message(filters.command("uptime"), sudo=True)
async def uptime_cmd(c: Client, m: Message):
    uptime = get_readable_time(int(time.time() - START_TIME))
    bot_me = await Tele.bot.get_me()
    bot_username = bot_me.username
    
    try:
        results = await c.get_inline_bot_results(bot_username, f"uptime {uptime}")
        if results.results:
            await c.send_inline_bot_result(
                m.chat.id,
                results.query_id,
                results.results[0].id
            )
            if m.from_user and m.from_user.id == c.me.id:
                try: await m.delete()
                except: pass
        else:
            raise ValueError("No results")
    except Exception as e:
        logger.error(f"Inline uptime failed: {e}")
        await m.reply(f"**Uptime -** `{uptime}`")

# --- Inline Handlers ---

@Tele.bot.on_inline_query(filters.regex(r"^ping (\d+) (.*)"))
async def ping_inline(c: Client, q: InlineQuery):
    latency = q.matches[0].group(1)
    uptime = q.matches[0].group(2)
    await q.answer([
        InlineQueryResultArticle(
            title="Ping",
            description=f"Latency: {latency}ms | Uptime: {uptime}",
            input_message_content=InputTextMessageContent(
                f"**Pong !!**\n"
                f"**Latency -** `{latency}ms`\n"
                f"**Uptime -** `{uptime}`"
            )
        )
    ], cache_time=0)

@Tele.bot.on_inline_query(filters.regex(r"^uptime (.*)"))
async def uptime_inline(c: Client, q: InlineQuery):
    uptime = q.matches[0].group(1)
    await q.answer([
        InlineQueryResultArticle(
            title="Uptime",
            description=f"Uptime: {uptime}",
            input_message_content=InputTextMessageContent(f"**Uptime -** `{uptime}`")
        )
    ], cache_time=0)

MOD_NAME = "Ping"
MOD_HELP = "**Usage:**\n> .ping - Check bot latency.\n> .uptime - Check bot uptime."
