from Hazel import Tele, START_TIME
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
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
async def pingFunc(c: Client, m: Message):
    start = time.time()
    end = time.time()
    latency = int((end - start) * 1000)
    uptime = get_readable_time(int(time.time() - START_TIME))
    
    return await m.reply(
        f"**Pong !!**\n"
        f"**Latency -** `{latency}ms`\n" # need change
        f"**Uptime -** `{uptime}`"
    )

MOD_NAME = "Ping"
MOD_HELP = "**Usage:**\n> .ping - Check Hazel's latency & uptime."
