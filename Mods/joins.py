from typing import List, Optional

from Hazel import Tele
import pyrogram
from pyrogram import enums
from pyrogram.types import Message, Chat
from pyrogram.errors import InviteRequestSent


@Tele.on_message(pyrogram.filters.command(["join", "leave"]), sudo=True)
async def joins_func(
    app: pyrogram.client.Client,
    m: Message
) -> None:

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


MOD_NAME: str = "joins"
MOD_HELP: str = (
    "> .join <link/username> - to join there\n"
    "> .leave <link/username/blank> - pass chat link or use in a group to leave from there."
)