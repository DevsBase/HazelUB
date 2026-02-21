from Hazel import SQLClient, Tele
from pyrogram.client import Client
from pyrogram.types import Message 
from pyrogram import filters
from bson import ObjectId

# ---------------- Repeat ----------------

@Tele.on_message(filters.command('repeat'), sudo=True)
async def repeatFunc(c: Client, m: Message):
    if m.from_user and m.from_user.id == c.me.id:
        try: await m.delete()
        except: pass
    if 'help' in str(m.text): 
        return await m.reply(MOD_HELP)
    text = m.text.split()  # type: ignore

    if len(text) < 3:
        return await m.reply("Usage: .repeat (minutes) (group_name)")

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
        return await m.reply("Group not found. Create one using .rgroup create (name)")

    try:
        await SQLClient.create_repeat_message(  
            repeatTime=mins,
            userId=c.me.id,  # type: ignore
            message_id=m.reply_to_message.id,  # type: ignore
            source_chat_id=m.reply_to_message.chat.id,  # type: ignore
            group_id=str(group["_id"])
        )
    except Exception as e:
        return await m.reply(f"Database error while creating repeat task: {e}")

    return await m.reply(
        f"Task created. Repeating every {mins} min in group `{group['name']}`."
    )


# ---------------- Groups ----------------

@Tele.on_message(filters.command('rgroup'), sudo=True)
async def groupCreate(c: Client, m: Message):
    if m.from_user and m.from_user.id == c.me.id:
        try: await m.delete()
        except: pass
    text = m.text.split(maxsplit=2)  # type: ignore

    if len(text) < 3 or text[1] != "create":
        return await m.reply("Usage: .rgroup create (name)")

    name = text[2]
    group = await SQLClient.get_group_by_name(name=name, user_id=c.me.id) # type: ignore
    if group:
        return await m.reply(f'You already have a group named `{name}`.')

    group = await SQLClient.create_group(  
        name,
        c.me.id  # type: ignore
    )

    return await m.reply(f"Group created: `{group['name']}` (id: {group['_id']})")


@Tele.on_message(filters.command('rgroup_add'), sudo=True)
async def groupAdd(c: Client, m: Message):
    if m.from_user and m.from_user.id == c.me.id:
        try: await m.delete()
        except: pass
    text = m.text.split(maxsplit=1)  # type: ignore

    if len(text) < 2:
        return await m.reply("Usage: .rgroup_add (group_name)")

    group_name = text[1]

    group = await SQLClient.get_group_by_name( 
        group_name,
        c.me.id  # type: ignore
    )

    if not group:
        return await m.reply("Group not found.")
    
    chats = await SQLClient.get_group_chats(str(group["_id"]), c.me.id) # type: ignore
    for chat_id in chats:
        if chat_id == m.chat.id: # type: ignore
            return await m.reply(f'This chat already in group `{group_name}`.')

    await SQLClient.add_chat_to_group(  
        str(group["_id"]),
        m.chat.id,  # type: ignore
        c.me.id     # type: ignore
    )

    return await m.reply(f"Chat added to group `{group['name']}`.")


@Tele.on_message(filters.command('rgroup_remove'), sudo=True)
async def groupRemove(c: Client, m: Message):
    if m.from_user and m.from_user.id == c.me.id:
        try: await m.delete()
        except: pass
    text = m.text.split(maxsplit=1)  # type: ignore

    if len(text) < 2:
        return await m.reply("Usage: .rgroup_remove (group_name)")

    group_name = text[1]

    group = await SQLClient.get_group_by_name( 
        group_name,
        c.me.id  # type: ignore
    )

    if not group:
        return await m.reply("Group not found.")

    await SQLClient.remove_chat_from_group(  
        str(group["_id"]),
        m.chat.id,  # type: ignore
        c.me.id     # type: ignore
    )

    return await m.reply(f"Chat removed from group `{group['name']}`.")


@Tele.on_message(filters.command('rgroup_list'), sudo=True)
async def groupList(c: Client, m: Message):
    if m.from_user and m.from_user.id == c.me.id:
        try: await m.delete()
        except: pass
    text = m.text.split(maxsplit=1)  # type: ignore

    if len(text) < 2:
        return await m.reply("Usage: .rgroup_list (group_name)")

    group_name = text[1]

    group = await SQLClient.get_group_by_name( 
        group_name,
        c.me.id  # type: ignore
    )

    if not group:
        return await m.reply("Group not found.")

    chats = await SQLClient.get_group_chats( 
        str(group["_id"]),
        c.me.id  # type: ignore
    )

    if not chats:
        return await m.reply("Group is empty.")

    msg = f"Chats in `{group['name']}`:\n"
    msg += "\n".join(f"`{x}`" for x in chats)
    return await m.reply(msg)

@Tele.on_message(filters.command('rgroup_list_all'), sudo=True)
async def groupListAll(c: Client, m: Message):
    if m.from_user and m.from_user.id == c.me.id:
        try: await m.delete()
        except: pass
    groups = await SQLClient.get_groups( 
        c.me.id  # type: ignore
    )

    if not groups:
        return await m.reply("You have no groups.")

    msg = "Your Groups:\n\n"

    for g in groups:
        msg += f"- {g['name']} (id: `{g['_id']}`)\n"

    return await m.reply(msg)


# ---------------- Repeat Management ----------------

@Tele.on_message(filters.command('repeat_delete'), sudo=True)
async def repeatDelete(c: Client, m: Message):
    if m.from_user and m.from_user.id == c.me.id:
        try: await m.delete()
        except: pass
    text = m.text.split()  # type: ignore

    if len(text) < 2:
        return await m.reply("Usage: .repeat_delete (id)")

    rid = text[1]
    try:
        await SQLClient.delete_repeat_message(rid) 
        return await m.reply("Repeat task deleted. Restart required.")
    except Exception as e:
        return await m.reply(f"Error: {e}")


@Tele.on_message(filters.command('repeat_list'), sudo=True)
async def repeatList(c: Client, m: Message):
    if m.from_user and m.from_user.id == c.me.id:
        try: await m.delete()
        except: pass
    rows = await SQLClient.get_repeat_messages()
    rows = [r for r in rows if r.get("userId") == c.me.id]  # type: ignore

    if not rows:
        return await m.reply("No repeat tasks found.")

    msg = "Your Repeat Tasks:\n\n"

    for r in rows:
        msg += (
            f"ID: `{r.get('_id')}`\n"
            f"Every: {r.get('repeatTime')} min\n"
            f"Group ID: `{r.get('group_id')}`\n"
            "----------------------\n"
        )

    return await m.reply(msg)

@Tele.on_message(filters.command(['rpause', 'rresume']), sudo=True)
async def pauseAndResumeFunc(c: Client, m: Message):
    if m.from_user and m.from_user.id == c.me.id:
        try: await m.delete()
        except: pass
    import Hazel.Tasks.messageRepeater as messageRepeater
    uid = c.me.id # type: ignore
    if uid not in messageRepeater.events:
        return await m.reply("Cannot find this client in active repeater tasks.")
    event = messageRepeater.events[uid]
    if 'resume' in m.command[0].lower(): # type: ignore
        if event.is_set():
            return await m.reply("Repeat tasks are not paused.")
        event.set()
        return await m.reply("Resumed all messageRepeat Tasks for you.")
    else:
        if not event.is_set():
            return await m.reply("Repeat Tasks are paused already.")
        event.clear()
        return await m.reply("Paused all messageRepeat Tasks for you.")

MOD_NAME = "Repeater"
MOD_HELP = """**Usage:**
> .repeat (mins) (group) - Repeat a message.
> .rgroup create (name) - Create a group.
> .rgroup_add (group) - Add current chat to group (to receive repeats).
> .rgroup_remove (group) - Remove current chat from group.
> .rgroup_list (group) - List chats in group.
> .rgroup_list_all - List all groups.
> .repeat_delete (id) - Delete repeat task.
> .repeat_list - List repeat tasks.
> .rpause - Pause repeats.
> .rresume - Resume repeats."""
