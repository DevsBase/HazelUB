"""
Repeat System Commands

$repeat (minutes) (group_name)
  Reply to a message to repeat it every (minutes) in a group.

$rgroup create (name)
  Create a new repeat group.

$rgroup_add (group_name)
  Add current chat to a group.

$rgroup_remove (group_name)
  Remove current chat from a group.

$rgroup_list (group_name)
  List all chats in a group.

$rgroup_list_all
  List all your repeat groups.

$repeat_delete (id)
  Delete a repeat task.

$repeat_list 
  List all repeating messages.
"""

from Hazel import SQLClient, Tele
from pyrogram.client import Client
from pyrogram.types import Message 
from pyrogram import filters
from sqlalchemy.exc import IntegrityError


# ---------------- Repeat ----------------

@Tele.on_message(filters.command('repeat') & filters.me)
async def repeatFunc(c: Client, m: Message):
    if 'help' in str(m.text): 
        return await m.reply(__doc__ or "No help.")
    text = m.text.split()  # type: ignore

    if len(text) < 3:
        return await m.reply("Usage: $repeat (minutes) (group_name)")

    if not m.reply_to_message:
        return await m.reply("Please reply to a message.")

    if not text[1].isdigit():
        return await m.reply("Invalid time. Must be number of minutes.")

    mins = int(text[1])
    if mins > 500:
        return await m.reply("You can only repeat maximum of 500 minutes.")

    group_name = text[2]

    group = await SQLClient.get_group_by_name( 
        group_name,
        c.me.id  # type: ignore
    )

    if not group:
        return await m.reply("Group not found. Create one using $rgroup create (name)")

    try:
        await SQLClient.create_repeat_message(  
            repeatTime=mins,
            userId=c.me.id,  # type: ignore
            message_id=m.reply_to_message.id,  # type: ignore
            source_chat_id=m.reply_to_message.chat.id,  # type: ignore
            group_id=group.id
        )
    except IntegrityError:
        return await m.reply("Database error while creating repeat task.")

    return await m.reply(
        f"Task created. Repeating every {mins} min in group `{group.name}`."
    )


# ---------------- Groups ----------------

@Tele.on_message(filters.command('rgroup') & filters.me)
async def groupCreate(c: Client, m: Message):
    text = m.text.split(maxsplit=2)  # type: ignore

    if len(text) < 3 or text[1] != "create":
        return await m.reply("Usage: $rgroup create (name)")

    name = text[2]
    group = await SQLClient.get_group_by_name(name=name, user_id=c.me.id) # type: ignore
    if group:
        return await m.reply(f'You already have a group named `{name}`.')

    group = await SQLClient.create_group(  
        name,
        c.me.id  # type: ignore
    )

    return await m.reply(f"Group created: `{group.name}` (id: {group.id})")


@Tele.on_message(filters.command('rgroup_add') & filters.me)
async def groupAdd(c: Client, m: Message):
    text = m.text.split(maxsplit=1)  # type: ignore

    if len(text) < 2:
        return await m.reply("Usage: $rgroup_add (group_name)")

    group_name = text[1]

    group = await SQLClient.get_group_by_name( 
        group_name,
        c.me.id  # type: ignore
    )

    if not group:
        return await m.reply("Group not found.")
    
    chats = await SQLClient.get_group_chats(group.id, c.me.id) # type: ignore
    for chat_id in chats:
        if chat_id == m.chat.id: # type: ignore
            return await m.reply(f'This chat already in group `{group_name}`.')

    await SQLClient.add_chat_to_group(  
        group.id,
        m.chat.id,  # type: ignore
        c.me.id     # type: ignore
    )

    return await m.reply(f"Chat added to group `{group.name}`.")


@Tele.on_message(filters.command('rgroup_remove') & filters.me)
async def groupRemove(c: Client, m: Message):
    text = m.text.split(maxsplit=1)  # type: ignore

    if len(text) < 2:
        return await m.reply("Usage: $rgroup_remove (group_name)")

    group_name = text[1]

    group = await SQLClient.get_group_by_name( 
        group_name,
        c.me.id  # type: ignore
    )

    if not group:
        return await m.reply("Group not found.")

    await SQLClient.remove_chat_from_group(  
        group.id,
        m.chat.id,  # type: ignore
        c.me.id     # type: ignore
    )

    return await m.reply(f"Chat removed from group `{group.name}`.")


@Tele.on_message(filters.command('rgroup_list') & filters.me)
async def groupList(c: Client, m: Message):
    text = m.text.split(maxsplit=1)  # type: ignore

    if len(text) < 2:
        return await m.reply("Usage: $rgroup_list (group_name)")

    group_name = text[1]

    group = await SQLClient.get_group_by_name( 
        group_name,
        c.me.id  # type: ignore
    )

    if not group:
        return await m.reply("Group not found.")

    chats = await SQLClient.get_group_chats( 
        group.id,
        c.me.id  # type: ignore
    )

    if not chats:
        return await m.reply("Group is empty.")

    msg = f"Chats in `{group.name}`:\n"
    msg += "\n".join(str(x) for x in chats)
    return await m.reply(msg)

@Tele.on_message(filters.command('rgroup_list_all') & filters.me)
async def groupListAll(c: Client, m: Message):
    groups = await SQLClient.get_groups( 
        c.me.id  # type: ignore
    )

    if not groups:
        return await m.reply("You have no groups.")

    msg = "Your Groups:\n\n"

    for g in groups:
        msg += f"- {g.name} (id: {g.id})\n"

    return await m.reply(msg)


# ---------------- Repeat Management ----------------

@Tele.on_message(filters.command('repeat_delete') & filters.me)
async def repeatDelete(c: Client, m: Message):
    text = m.text.split()  # type: ignore

    if len(text) < 2:
        return await m.reply("Usage: $repeat_delete (id)")

    rid = int(text[1])
    await SQLClient.delete_repeat_message(rid) 
    return await m.reply("Repeat task deleted. Restart required.")


@Tele.on_message(filters.command('repeat_list') & filters.me)
async def repeatList(c: Client, m: Message):
    rows = await SQLClient.get_repeat_messages()

    rows = [r for r in rows if r.userId == c.me.id]  # type: ignore

    if not rows:
        return await m.reply("No repeat tasks found.")

    msg = "Your Repeat Tasks:\n\n"

    for r in rows:
        msg += (
            f"ID: {r.id}\n"
            f"Every: {r.repeatTime} min\n"
            f"Group ID: {r.group_id}\n"
            "----------------------\n"
        )

    return await m.reply(msg)