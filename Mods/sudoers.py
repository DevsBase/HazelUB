from pyrogram import Client, filters
from pyrogram.types import Message
from Hazel import Tele, SQLClient

@Tele.on_message(filters.command("addsudo"), sudo=True)
async def addsudo_handler(c: Client, m: Message):
    if m.reply_to_message and hasattr(m.reply_to_message.from_user, 'id'):
        user_id = m.reply_to_message.from_user.id
    else:
        return await m.reply("Reply to a user to add sudo.")
        
    added = await SQLClient.add_sudo(user_id)
    if added:
        await m.reply(f"Added user `{user_id}` to sudoers. Restart required.")
    else:
        await m.reply(f"User `{user_id}` is already a sudoer.")

@Tele.on_message(filters.command("delsudo"), sudo=True)
async def delsudo_handler(c: Client, m: Message):
    if m.reply_to_message:
        user_id = m.reply_to_message.from_user.id
    else:
        args = m.text.split()
        if len(args) < 2:
            return await m.reply("Reply to a user or provide user ID.")
        try:
            user_id = int(args[1])
        except ValueError:
            return await m.reply("Invalid User ID.")
            
    await SQLClient.remove_sudo(user_id)
    await m.reply(f"Removed user `{user_id}` from sudoers. Restart required.")

@Tele.on_message(filters.command("sudoers"), sudo=True)
async def sudoers_handler(c: Client, m: Message):
    sudoers = await SQLClient.get_sudoers()
    if not sudoers:
        return await m.reply("No sudo users found.")
    
    text = "**Sudo Users:**\n"
    for user_id in sudoers:
        text += f"- `{user_id}`\n"
    await m.reply(text)

MOD_NAME = "Sudoers"
MOD_HELP = """**Usage:**
> .addsudo (reply) - Add a user to sudoers.
> .delsudo (ID/reply) - Remove a user from sudoers.
> .sudoers - List all sudoers."""
