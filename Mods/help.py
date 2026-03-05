import importlib
import logging
import os

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    Message,
)

from Hazel import Tele
from Hazel.enums import USABLE, WORKS, CombinedValue
from Hazel.ModLoader import MODS_DATA

logger = logging.getLogger(__name__)


def get_help_markup(page_num: int = 0) -> tuple[InlineKeyboardMarkup | None, int]:
    mod_names = sorted(MODS_DATA.keys())
    page_size = 10
    total_pages = (len(mod_names) + page_size - 1) // page_size

    if total_pages == 0:
        return None, 0

    if page_num < 0:
        page_num = 0
    if page_num >= total_pages:
        page_num = total_pages - 1

    start = page_num * page_size
    end = start + page_size
    items = mod_names[start:end]

    buttons: list[list[InlineKeyboardButton]] = []
    for i in range(0, len(items), 2):
        row: list[InlineKeyboardButton] = []
        for j in range(i, min(i + 2, len(items))):
            row.append(
                InlineKeyboardButton(
                    items[j], callback_data=f"hmod_{items[j]}_{page_num}"
                )
            )
        buttons.append(row)

    nav: list[InlineKeyboardButton] = []
    if page_num > 0:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"hpage_{page_num-1}"))

    nav.append(
        InlineKeyboardButton(f"Page {page_num+1}/{total_pages}", callback_data="none")
    )

    if page_num < total_pages - 1:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"hpage_{page_num+1}"))

    buttons.append(nav)
    buttons.append([InlineKeyboardButton("> HazelUB <", callback_data="none")])
    return InlineKeyboardMarkup(buttons), len(mod_names)


@Tele.on_message(filters.command("help"), sudo=True)
async def help_userbot(c: Client, m: Message):
    try:
        if c.me and c.me.is_bot:
            markup, count = get_help_markup(0)
            if markup:
                await m.reply(
                    f"• **Help Menu**\n\nTotal Modules: `{count}`", reply_markup=markup
                )
            return

        bot = Tele.bot
        if not bot or not bot.me or not bot.me.username:
            await m.edit("Bot client is not initialized.")
            return

        bot_username = bot.me.username
        results = await c.get_inline_bot_results(bot_username, "help")
        
        if results and results.results and len(results.results) > 0:
            query_id = results.query_id
            result_id = results.results[0].id
            if not m.chat:
                return
            chat_id = m.chat.id

            if query_id and result_id and chat_id:
                await c.send_inline_bot_result(
                    chat_id=chat_id,
                    query_id=query_id,
                    result_id=result_id
                )
                await m.delete()
                return
                
        await m.edit("No results from bot. Make sure inline mode is enabled.")

    except Exception as e:
        error_msg = str(e)
        if "CHAT_SEND_INLINE_FORBIDDEN" in error_msg:
            await m.reply("Sending inline messages is not allowed in this chat.")
        elif "BOT_INLINE_DISABLED" in error_msg:
            bot_uname = Tele.bot.me.username if Tele.bot and Tele.bot.me else "Bot"
            await m.reply(f"Please enable inline mode for @{bot_uname} in @BotFather")
        else:
            logging.error(f"Error while sending help menu: {e}")
            await m.edit(
                f"**HazelUB Help**\n\nError: {e}\nMake sure inline mode is enabled for the bot."
            )


@Tele.bot.on_inline_query(filters.regex("help"))
async def help_inline(c: Client, q: InlineQuery):
    markup, count = get_help_markup(0)
    if not markup:
        return await Tele.inline(q).answer_text(title="No modules found", text="No modules with help found.")

    await Tele.inline(q).answer_text(
        title="• Help Menu",
        text=f"• **Help Menu**\n\nTotal Modules: `{count}`",
        reply_markup=markup
    )


@Tele.bot.on_callback_query(filters.regex(r"^hpage_(\d+)$"))
async def help_page_cb(c: Client, q: CallbackQuery):
    if not q.matches:
        return
        
    page_num = int(q.matches[0].group(1))
    markup, count = get_help_markup(page_num)
    
    if not markup:
        return
    
    if c.me and c.me.is_bot and q.message:
        return await q.message.edit(
            text=f"• **Help Menu**\n\nTotal Modules: `{count}`",
            reply_markup=markup,
        )    
    await q.edit_message_text(
        text=f"• **Help Menu**\n\nTotal Modules: `{count}`",
        reply_markup=markup,
    )


@Tele.bot.on_callback_query(filters.regex(r"^hmod_(.*)_(\d+)$"))
async def help_mod_cb(c: Client, q: CallbackQuery):
    if not q.matches:
        return
        
    mod_name = q.matches[0].group(1)
    page_num = int(q.matches[0].group(2))
    
    help_data = MODS_DATA.get(mod_name)
    if not help_data:
        help_text = "No help found."
        usable = "Unknown"
        works = "Unknown"
    else:
        help_text = help_data.get("help", "No help found.")
        u_val = help_data.get("usable")
        w_val = help_data.get("works")
        
        if isinstance(u_val, USABLE) or isinstance(u_val, CombinedValue):
            u_val = u_val.value
        if isinstance(w_val, WORKS) or isinstance(w_val, CombinedValue):
            w_val = w_val.value
        
        usable = getattr(u_val, "name", str(u_val)) if u_val else "Unknown"
        works = getattr(w_val, "name", str(w_val)) if w_val else "Unknown"

    buttons = [
        [InlineKeyboardButton(f"👤 Usable By: {usable}", callback_data="none")],
        [InlineKeyboardButton(f"🌍 Works In: {works}", callback_data="none")],
        [InlineKeyboardButton("⬅️ Back", callback_data=f"hpage_{page_num}")]
    ]
    
    if c.me and c.me.is_bot and q.message:
        return await q.message.edit(
            text=f"**Module:** {mod_name}\n\n{help_text}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    await q.edit_message_text(
        text=f"**Module:** {mod_name}\n\n{help_text}",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@Tele.bot.on_callback_query(filters.regex("none"))
async def none_cb(c: Client, q: CallbackQuery):
    await q.answer()

MOD_CONFIG = {
    "name": "Help",
    "help": "Shows this help menu.\n\nUsage: `.help`",
    "works": WORKS.ALL,
    "usable": USABLE.ALL
}