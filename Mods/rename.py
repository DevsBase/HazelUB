from Hazel import Tele
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
from Hazel.enums import USABLE, WORKS
import asyncio
import os

@Tele.on_message(filters.command("rename"), sudo=True)
async def rename_func(c: Client, m: Message):     
    if not m.command or m.command and len(m.command) < 2:
        return await m.reply("Usage: `.rename <new caption>`")
    
    if reply := m.reply_to_message:
        if not reply.media:
            return await m.reply("Reply to a media message to rename it.")
        file_name = " ".join(m.command[1:])
        status = await m.reply("Downloading...")
        try:
            path = await reply.download(file_name=file_name)
            await Tele.message(status).edit("Uploading...", business_connection_id=m.business_connection_id)
            await m.reply_document(path)
            asyncio.create_task(asyncio.to_thread(os.remove, path))
            await Tele.message(status).delete(business_connection_id=m.business_connection_id)   
        except Exception as e:
            await Tele.message(status).edit(f"**Error:** {e}")
    else:
        return await m.reply("Reply to a message to rename it.")
    
MOD_CONFIG = {
    "name": "rename",
    "help": (
        "**Usage:**\n"
        "> .rename (reply media & new file name) - to rename files"
    ),
    "usable": USABLE.OWNER & USABLE.SUDO,
    "works": WORKS.ALL
}