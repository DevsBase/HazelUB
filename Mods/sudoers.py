from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
from Hazel import Tele, SQLClient, sudoers
import Hazel

@Tele.on_message(filters.command("asudo"), sudo=True)
async def addsudo_handler(c: Client, m: Message):
    if m.reply_to_message and hasattr(m.reply_to_message.from_user, 'id'):
        user_id = m.reply_to_message.from_user.id # type: ignore
    else:
        return await m.reply("Reply to a user to add sudo.")
    
    if not c.me:
        return
    owner_id = c.me.id
    
    for client in Tele._allClients:
        if client.me and client.me.id == user_id:
            return await m.reply("This user is already a HazelUB user. Please remove their session in config.py or .env to use this command.")
        
    added = await SQLClient.add_sudo(owner_id, user_id)
    if added:
        if owner_id not in sudoers:
            Hazel.sudoers[owner_id] = []
        if user_id not in sudoers[owner_id]:
            Hazel.sudoers[owner_id].append(user_id)
        await m.reply(f"Added user `{user_id}` as sudo for this client.")
    else:
        await m.reply(f"User `{user_id}` is already a sudoer for this client.")

@Tele.on_message(filters.command("rsudo"), sudo=True)
async def delsudo_handler(c: Client, m: Message):
    if not c.me:
        return
    owner_id = c.me.id
    if m.reply_to_message:
        user_id = m.reply_to_message.from_user.id if m.reply_to_message.from_user else 0
    else:
        args = m.text.split() if m.text else []
        if len(args) < 2:
            return await m.reply("Reply to a user or provide user ID.")
        try:
            user_id = int(args[1])
        except ValueError:
            return await m.reply("Invalid User ID.")
    
    if not user_id:
        return await m.reply("Could not get user ID.")
            
    await SQLClient.remove_sudo(owner_id, user_id)
    if owner_id in sudoers and user_id in sudoers[owner_id]:
        Hazel.sudoers[owner_id].remove(user_id)
    await m.reply(f"Removed user `{user_id}` from sudoers for this client.")

@Tele.on_message(filters.command("sudoers"), sudo=True)
async def sudoers_handler(c: Client, m: Message):
    if not c.me:
        return
    owner_id = c.me.id
    client_sudoers = await SQLClient.get_sudoers(owner_id)
    if not client_sudoers:
        return await m.reply("No sudo users found.")
    
    text = f"**Sudo Users for {c.me.first_name}:**\n"
    for user_id in client_sudoers:
        text += f"- `{user_id}`\n"
    await m.reply(text)

MOD_NAME = "Sudoers"
MOD_HELP = """**Usage:**
> .asudo (reply) - Add a user to sudoers. Restart required.
> .dsudo (ID/reply) - Remove a user from sudoers. Restart required.
> .sudoers - List all sudoers."""
