from Hazel.enums import USABLE, WORKS
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
from Hazel import Tele, WA


@Tele.on_message(filters.command("connectwa"), sudo=True)
async def whatsapp_connect_cmd(c: Client, m: Message):
    if Tele.getClientPrivilege(c) != "sudo":
        return await m.reply("This client don't have `sudo` privillage. It is required to use this command.")
    await m.reply("Please scan the QR code shown in the terminal.")
    for client in WA._allClients:
        await WA.connect_neonize_client(client)

help_text = """**Usage:**
> soon
"""

MOD_CONFIG = {
    "name": "Whatsapp",
    "help": help_text,
    "works": WORKS.ALL,
    "usable": USABLE.ALL,
}