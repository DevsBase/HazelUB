from Hazel import Tele
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
from pyrogram.raw.functions.ping import Ping
import time
import logging
from config import START_TIME

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

    # Measure MTProto RTT
    start = time.perf_counter()
    await c.invoke(Ping(ping_id=int(time.time())))
    end = time.perf_counter()

    latency = round((end - start) * 1000, 2)
    uptime = get_readable_time(int(time.time() - START_TIME))

    return await m.reply(
        f"**Pong !!**\n"
        f"**Latency -** `{latency} ms`\n"
        f"**Uptime -** `{uptime}`"
    )


MOD_NAME = "Ping"
MOD_HELP = "**Usage:**\n> .ping - Check Hazel's latency & uptime."