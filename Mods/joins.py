from Hazel.enums import USABLE, WORKS
from typing import List, Optional

from Hazel import Tele
import pyrogram
from pyrogram import enums
from pyrogram.types import Chat
from pyrogram.errors import InviteRequestSent
from pyrogram.types import (
    InlineQuery,
    Message,
)

@Tele.on_message(pyrogram.filters.command(["join", "leave"]), sudo=True)
async def joins_func(
    app: pyrogram.client.Client,
    m: Message
) -> None:
    
    if app.me and app.me.is_bot and m.from_user:
        app = Tele.getClientById(m.from_user.id) or app
        
    command: Optional[List[str]] = m.command
    text: str = m.text or ""

    if not command:
        return

    action: str = command[0].lower()

    if (
        action == "leave"
        and len(command) < 2
        and m.chat is not None
        and m.chat.id is not None
        and m.chat.type not in (enums.ChatType.BOT, enums.ChatType.PRIVATE)
    ):
        if "-silent" in text.lower():
            await m.delete()
        else:
            title: str = m.chat.title or "this chat"
            await m.reply(f"Left from {title}.")

        await app.leave_chat(m.chat.id)
        return

    if len(command) < 2:
        await m.reply(f"Need username/link to {action}.")
        return

    link: str = command[1]

    if action == "join":
        try:
            result = await app.join_chat(link)

            if isinstance(result, Chat):
                title: str = result.title or "Unknown"
                await m.reply(f"Joined, {title}.")
            else:
                await m.reply("Joined.")

        except InviteRequestSent:
            await m.reply("Join request sent.")
        except Exception as e:
            await m.reply(f"Failed: {e}")

        return

    try:
        result = await app.leave_chat(link)

        if isinstance(result, Chat):
            title: str = result.title or "Unknown"
            await m.reply(f"Left from {title}.")
        else:
            await m.reply("Left successfully.")

    except Exception as e:
        await m.reply(f"Failed: {e}")


@Tele.bot.on_inline_query(pyrogram.filters.regex(r"^join"))
async def joinInlineFunc(c: pyrogram.client.Client, q: InlineQuery):
    chat_username = q.query.split(None, 1)[1] if len(q.query.split(None, 1)) > 1 else None
    if not chat_username:
        await Tele.inline(q).answer_text("No chat specified", "Please provide a chat username or link")
        return
    
    join_client = Tele.getClientById(q.from_user.id)
    if not join_client:
        await Tele.inline(q).answer_text("No Client found", "You don't have an active client session.")
        return
    
    try:
        x = await join_client.join_chat(chat_username)
        await Tele.inline(q).answer_text("Joined", f"Joined {x.first_name} successfully.")
    except Exception as e:
        await Tele.inline(q).answer_text("Failed", f"Failed to join: {e}")

MOD_CONFIG = {
    "name": "Joins",
    "help": (
        "**Usage:**\n"
        "> .join [username/link] - Join a group/channel.\n"
        "> .leave [username/link, __optional__] - Leave a group/channel. \n\n"
        "You can also use `-silent` with leave command to avoid sending a message after leaving."
    ),
    "works": WORKS.ALL,
    "usable": USABLE.ALL
}