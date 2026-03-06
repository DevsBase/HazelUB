from Hazel import Tele
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message, InlineQuery
from Hazel.enums import USABLE, WORKS

@Tele.on_message(filters.command("repo"), sudo=True)
@Tele.on_inline_query(filters.regex(r"^repo"), sudo=True)
async def repoFunc(c: Client, m: Message | InlineQuery):
    if isinstance(m, Message):
        if m.reply_to_message:
            m = m.reply_to_message
    await Tele.message(m).reply("https://github.com/DevsBase/HazelUB")

MOD_CONFIG = {
    "name": "Misc",
    "help": (
        "**Usage:**\n"
        "> .repo - to get the repo link."
    ),
    "works": WORKS.ALL,
    "usable": USABLE.ALL
}