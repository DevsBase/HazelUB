from Hazel.enums import USABLE, WORKS
from pyrogram.client import Client
from urllib.parse import urlparse
from Hazel import Tele
from pyrogram import filters, types
import webbrowser
import asyncio


@Tele.on_message(filters.command("open"), sudo=True)
async def openCommand(client: Client, m: types.Message):
    if not m or not m.from_user:
        return
    if Tele.getClientPrivilege(user_id=m.from_user.id) != "sudo":
        return await m.reply(
            "This client don't have `sudo` privillage. It is required to use this command."
        )
    if not m.text:
        return await m.reply("Provide a link to open.")
    link = m.text.split(None, 1)
    if len(link) == 1:
        return await m.reply("Provide a link to open.")
    try:
        if not urlparse(link[1]).scheme:
            link[1] = "https://" + link[1]
        await asyncio.to_thread(webbrowser.open, link[1])
        await m.reply(f"Opened __{link[1]}__ successfully.")
    except Exception as e:
        await m.reply(f"Failed to open link.\n\n**Error:** {e}")

MOD_CONFIG = {
    "name": "Web-Tools",
    "help": "**Usage:**\n> .open (link) - Open a link in server/machine browser.",
    "works": WORKS.ALL,
    "usable": USABLE.ALL
}
