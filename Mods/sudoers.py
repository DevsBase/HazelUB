from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
from Hazel import Tele, SQLClient, sudoers

@Tele.on_message(filters.command("addsudo"), sudo=True)
async def addsudo_handler(c: Client, m: Message):
    if m.reply_to_message and hasattr(m.reply_to_message.from_user, 'id'):
        user_id = m.reply_to_message.from_user.id # type: ignore
    else:
        return await m.reply("Reply to a user to add sudo.")
    
    owner_id = c.me.id # type: ignore
    
    for client in Tele._allClients:
        if hasattr(client.me, 'id'):
            if getattr(client.me, 'id') == user_id:
                return await m.reply("This user is already a HazelUB user. Please remove their session in config.py or .env to use this command.")
        
    added = await SQLClient.add_sudo(owner_id, user_id)
    if added:
        if owner_id not in sudoers:
            sudoers[owner_id] = []
        if user_id not in sudoers[owner_id]:
            sudoers[owner_id].append(user_id)
        await m.reply(f"Added user `{user_id}` as sudo for this client.")
    else:
        await m.reply(f"User `{user_id}` is already a sudoer for this client.")

@Tele.on_message(filters.command("delsudo"), sudo=True)
async def delsudo_handler(c: Client, m: Message):
    owner_id = c.me.id # type: ignore
    if m.reply_to_message:
        user_id = m.reply_to_message.from_user.id # type: ignore
    else:
        args = m.text.split() # type: ignore
        if len(args) < 2:
            return await m.reply("Reply to a user or provide user ID.")
        try:
            user_id = int(args[1])
        except ValueError:
            return await m.reply("Invalid User ID.")
            
    await SQLClient.remove_sudo(owner_id, user_id)
    if owner_id in sudoers and user_id in sudoers[owner_id]:
        sudoers[owner_id].remove(user_id)
    await m.reply(f"Removed user `{user_id}` from sudoers for this client.")

@Tele.on_message(filters.command("sudoers"), sudo=True)
async def sudoers_handler(c: Client, m: Message):
    owner_id = c.me.id # type: ignore
    client_sudoers = await SQLClient.get_sudoers(owner_id)
    if not client_sudoers:
        return await m.reply("No sudo users found for this client.")
    
    text = f"**Sudo Users for {c.me.first_name}:**\n"
    for user_id in client_sudoers:
        text += f"- `{user_id}`\n"
    await m.reply(text)

MOD_NAME = "Sudoers"
MOD_HELP = """**Usage:**
> .addsudo (reply) - Add a user to sudoers for the current client.
> .delsudo (ID/reply) - Remove a user from sudoers for the current client.
> .sudoers - List all sudoers for the current client."""
