from pyrogram.client import Client
from urllib.parse import urlparse
from Hazel import Tele
from pyrogram import filters
import webbrowser
import asyncio

@Tele.on_message(filters.command('open') & filters.me)
async def openCommand(client, m):
    if Tele.getClientPrivilege(client) != 'sudo':
        return await m.reply("You don't have permission.")
    
    link = m.text.split(None, 1)
    if len(link) == 1:
       return await m.reply('Provide a link to open.')
    try:
        if not urlparse(link[1]).scheme:
            link[1] = "https://" + link[1]
        await asyncio.to_thread(webbrowser.open, link[1])
        await m.reply(f'Opened __{link[1]}__ successfully.')
    except Exception as e:
        await m.reply(f'Failed to open link.\n\n**Error:** {e}')

"""
    Try on your machine. It won't work on servers untill broswer is installed.
    You can also use it to open files by providing file path instead of url.
    Example: $open C:\Users\user\Desktop\file.txt
"""