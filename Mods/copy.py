from Hazel import Tele
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
from Hazel.enums import USABLE, WORKS

copy_data: dict[int, Message]= {}

@Tele.on_message(filters.command(["copy", "cp"]), sudo=True)
async def copy_cmd(c: Client, m: Message):
    global copy_data
    if not m.reply_to_message:
        return await m.reply("Reply to a message to copy it.")
    if m.from_user:
        copy_data[m.from_user.id] = m.reply_to_message
        await m.reply("Copied!")

@Tele.on_message(filters.command(["paste", "ps", "nps"]), sudo=True)
async def paste_cmd(c: Client, m: Message):
    if not m.from_user or not m.chat or not m.chat.id:
        return
    if not copy_data.get(m.from_user.id):
        return await m.reply("Clipboard is empty.")
    if m.text and "nps" in m.text:
        return await copy_data[m.from_user.id].copy(m.chat.id, caption="")
    await copy_data[m.from_user.id].copy(m.chat.id)

MOD_CONFIG = {
    "name": "Copy Paste",
    "help": (
        "**Usage:**\n"
        "> .copy / .cp - to copy a message (reply to a message with this command).\n"
        "> .paste / .ps - to paste the copied message.\n"
        "> .nps - to paste the copied message without caption (only for media)."
    ),
    "works": WORKS.ALL,
    "usable": USABLE.OWNER and USABLE.SUDO
}