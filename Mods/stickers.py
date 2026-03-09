from Hazel.enums import USABLE, WORKS
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
from Hazel import Tele

@Tele.on_message(filters.command("kang"), sudo=True)
async def kang_cmd(c: Client, m: Message):
    ...
    
MOD_CONFIG = {
    "name": "Kang",
    "help": (
        "**Usage:**\n"
        "> .kang (reply) [emoji, __optional__] - To kang that replied sticker."
    ),
    "group": "Stickers",
    "works": WORKS.ALL,
    "usable": USABLE.OWNER & USABLE.SUDO & USABLE.BOT,
    "required_mods": ["settings.py"]
}