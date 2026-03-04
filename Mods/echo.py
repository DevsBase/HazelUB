from Hazel.enums import USABLE, WORKS
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
from Hazel import Tele

@Tele.on_message(filters.command(["echo", "ec"]), sudo=True)
async def echo_cmd(c: Client, m: Message):
    if m.reply_to_message and m.chat and m.chat.id:
        await m.reply_to_message.copy(m.chat.id)
    try: await m.delete()
    except: ...

MOD_CONFIG = {
    "name": "Echo",
    "help": "> .echo / .ec (reply) - to send the replied message.",
    "works": WORKS.ALL,
    "usable": USABLE.ALL
}
