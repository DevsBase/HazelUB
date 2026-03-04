from Hazel.enums import USABLE, WORKS
from typing import List, Optional

from Hazel import Tele
import pyrogram
from pyrogram import enums
from pyrogram.types import Message, Chat
from pyrogram.errors import InviteRequestSent
from MultiSessionManagement.decorators import sudo_check
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
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


@Tele.bot.on_inline_query(pyrogram.filters.regex("join"))
async def joinInlineFunc(c: pyrogram.client.Client, q: InlineQuery):
    btns = InlineKeyboardMarkup([[InlineKeyboardButton("Verify", callback_data="join_chat")]])
    await q.answer(
        [
            InlineQueryResultArticle(
                title="Join a chat",
                description="Click the button to verify and join the chat.",
                input_message_content=InputTextMessageContent("Click the button below to verify and join the chat."),
                reply_markup=btns
            )
        ],
    )

@Tele.bot.on_callback_query(pyrogram.filters.regex("join_chat"))
async def joinChatCallback(c: pyrogram.client.Client, q: CallbackQuery):
    if not await sudo_check(None, c, q.message):
        await q.answer("You cannot access this userbot.")
    if not q.message.chat or not q.message.chat.username:
        return await q.answer("Chat not found or it is private.")
    
    chat = q.message.chat.username

    join_client = Tele.getClientById(q.from_user.id)
    if not join_client:
        return await q.answer("Client not found.")
    try:
        await join_client.join_chat(chat)
        await q.edit_message_text("Joined.")
    except Exception as e:
        await q.edit_message_text(str(e))



MOD_NAME: str = "joins"
MOD_HELP: str = (
    "> .join <link/username> - to join there\n"
    "> .leave <link/username/blank> - pass chat link or use in a group to leave from there."
)
MOD_WORKS = WORKS.ALL
MOD_USABLE = USABLE.ALL