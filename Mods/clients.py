"""This module is to manage other clients/users in your HazelUB.

.asudo (reply to a user) - To give them sudo privilage.
.rsudo (reply to a user) - To remove sudo privilage.
.clients - To get all clients/users connected in HazelUB.

**⚠️ Warning:** Do not give sudo access to anyone unless it's you or a trusted person. Anyone can steal your session using this, Plus. they can hack the userbot's system and your telegram account.
"""

from pyrogram.client import Client
from pyrogram import filters
from pyrogram.types import Message
from Hazel import Tele, __version__

infoTxt = """
![👤](tg://emoji?id=5258011929993026890) **Name:** - **{}**
![ℹ️](tg://emoji?id=4967518033061872209) **User ID:** `{}`
![🖱](tg://emoji?id=4970107898341360413) **Privilege:** {}
"""

@Tele.on_message(filters.command('clients') & filters.me)
async def clientsFunc(c: Client, m: Message):
    txt = "**Clients informations**\n"
    for client in Tele._allClients:
        if client.me:
            txt += infoTxt.format(client.me.first_name, client.me.id, getattr(client, 'privilege', 'user')) # type: ignore
    txt += f"**HazelUB v{__version__}**"
    await m.reply(txt)

@Tele.on_message(filters.command('asudo') & filters.me)
async def add_sudo(c: Client, m: Message):
    if Tele.getClientPrivilege(c) != 'sudo':
        return await m.reply("You don't have permisson.")
    if not m.reply_to_message:
        if len(m.command or []) < 2:
            return await m.reply("Reply or enter id.")
        uid = int(m.text.split(None, 1)[1]) # type: ignore
    else:
        uid = m.reply_to_message.from_user.id # type: ignore
    
    client = Tele.getClientById(uid)
    if client:
        if Tele.getClientPrivilege(client) != "sudo":           
            Tele._clientPrivileges[client] = 'sudo'
            return await m.reply("Promoted.")
        else: 
            return await m.reply("They already have `sudo` privilege.")
    return await m.reply("Client not found. You should add their session in OtherSessions in config.py or env.")
        

@Tele.on_message(filters.command('rsudo') & filters.me)
async def remove_sudo(c: Client, m: Message):
    if Tele.getClientPrivilege(c) != 'sudo':
        return await m.reply("You don't have permisson.")
    if not m.reply_to_message:
        if len(m.command or []) < 2:
            return await m.reply("Reply or enter id.")
        uid = int(m.text.split(None, 1)[1]) # type: ignore
    else:
        uid = m.reply_to_message.from_user.id # type: ignore
    
    client = Tele.getClientById(uid)
    if client:
        if Tele.getClientPrivilege(client) == "sudo":           
            Tele._clientPrivileges[client] = 'user'
            return await m.reply("Demoted.")
        else: 
            return await m.reply("They already don't have `sudo` privilege.")
    return await m.reply("Client not found. You should add their session in OtherSessions in config.py or env.")

MOD_NAME = "Clients"
MOD_HELP = """**Usage:**
> .clients - Info about all sessions.
> .asudo - Add sudo (reply).
> .rsudo - Remove sudo (reply)."""
