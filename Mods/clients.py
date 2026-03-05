from Hazel.enums import USABLE, WORKS
from pyrogram.client import Client
from pyrogram import filters
from pyrogram.types import Message
from Hazel import Tele, __version__

infoTxt = """
![👤](tg://emoji?id=5258011929993026890) **Name:** - **{}**
![🆔](tg://emoji?id=4967518033061872209) **User ID:** `{}`
![👮](tg://emoji?id=4970107898341360413) **Privilege:** {}
🧑🏻‍💻 **Connected:** {}
"""


@Tele.on_message(filters.command("clients"), sudo=True)
async def clientsFunc(c: Client, m: Message):
    txt = "• **Hazel Clients:**\n"

    for client in Tele._allClients:
        if client.me:
            txt += infoTxt.format(client.me.first_name, client.me.id, Tele.getClientPrivilege(client), client.is_connected)  # type: ignore

    txt += f"\nHazelUB `v{__version__}`"
    await m.reply(txt)


@Tele.on_message(filters.command("cpromote"), sudo=True, bot=False)
async def add_sudo(c: Client, m: Message):
    if not m or not m.from_user:
        return
    if Tele.getClientPrivilege(user_id=m.from_user.id) != "sudo":
        return await m.reply(
            "This client don't have `sudo` privillage. It is required to use this command."
        )

    if not m.reply_to_message:
        if len(m.command or []) < 2:
            return await m.reply("Reply or enter id.")
        uid = int(m.text.split(None, 1)[1])  # type: ignore

    else:
        uid = m.reply_to_message.from_user.id  # type: ignore

    client = Tele.getClientById(uid)
    if client:
        if Tele.getClientPrivilege(client) != "sudo":
            Tele._clientPrivileges[client] = "sudo"
            return await m.reply("Promoted.")
        else:
            return await m.reply("They already have `sudo` privilege.")
    return await m.reply(
        "Client not found. You should add their session in OtherSessions in config.py or env."
    )


@Tele.on_message(filters.command("cdemote"), sudo=True, bot=False)
async def remove_sudo(c: Client, m: Message):
    if not m or not m.from_user:
        return
    if Tele.getClientPrivilege(user_id=m.from_user.id) != "sudo":
        return await m.reply(
            "This client don't have `sudo` privillage. It is required to use this command."
        )

    if not m.reply_to_message:
        if len(m.command or []) < 2:
            return await m.reply("Reply or enter id.")
        uid = int(m.text.split(None, 1)[1])  # type: ignore

    else:
        uid = m.reply_to_message.from_user.id  # type: ignore

    client = Tele.getClientById(uid)
    if client:
        if Tele.getClientPrivilege(client) == "sudo":
            Tele._clientPrivileges[client] = "user"
            if not any(
                Tele.getClientPrivilege(_c) == "sudo" for _c in Tele._allClients
            ):
                Tele._clientPrivileges[client] = "sudo"
                return await m.reply(
                    "The client is demoted and promoted back because no other client will have `sudo` privillage. Please promote any other client and demote it."
                )
            return await m.reply("Demoted.")
        else:
            return await m.reply("They already don't have `sudo` privilege.")
    return await m.reply(
        "Client not found. You should add their session in OtherSessions in config.py or env."
    )


help = """**Usage:**
> .clients - Info about all sessions.
> .cpromote - Add sudo (reply). (Business bot won't work.)
> .cdemote - Remove sudo (reply). (Business bot won't work.)

**⚠️ Warning:** Do not give sudo access to anyone unless it's you or a trusted person. Anyone can steal your session using this, Plus. they can hack the userbot's system and your telegram account.
"""
MOD_CONFIG = {
    "name": "Clients",
    "help": help,
    "works": WORKS.ALL,
    "usable": USABLE.OWNER & USABLE.SUDO
}