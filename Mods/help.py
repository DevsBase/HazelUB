import Hazel
from pyrogram.client import Client
from pyrogram import filters
from pyrogram.types import (
    Message, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    CallbackQuery, 
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent
)
import os
import importlib
import logging
import sys

logger = logging.getLogger("Hazel.Help")

MODS_HELP = {}
BOT_INFO = {"username": None}

def load_mods_help():
    global MODS_HELP
    if MODS_HELP:
        return MODS_HELP
    
    mods_dir = os.path.dirname(__file__)
    for file in os.listdir(mods_dir):
        if file.endswith(".py") and not file.startswith("_") and file != "help.py":
            mod_name_id = file[:-3]
            module_path = f"Mods.{mod_name_id}"
            try:
                if module_path in sys.modules:
                    module = sys.modules[module_path]
                else:
                    module = importlib.import_module(module_path)
                
                name = getattr(module, "MOD_NAME", mod_name_id.replace('-', ' ').capitalize())
                help_text = getattr(module, "MOD_HELP", None)
                if help_text:
                    MODS_HELP[name] = help_text
            except Exception as e:
                logger.error(f"Error loading help for {module_path}: {e}")
    return MODS_HELP

def get_help_markup(page_num=0):
    mods = load_mods_help()
    mod_names = sorted(mods.keys())
    page_size = 10
    total_pages = (len(mod_names) + page_size - 1) // page_size
    if total_pages == 0: return None, 0
    
    if page_num < 0: page_num = 0
    if page_num >= total_pages: page_num = total_pages - 1
    
    start = page_num * page_size
    end = start + page_size
    items = mod_names[start:end]
    
    buttons = []
    for i in range(0, len(items), 2):
        row = []
        for j in range(i, min(i+2, len(items))):
            row.append(InlineKeyboardButton(items[j], callback_data=f"hmod_{items[j]}_{page_num}"))
        buttons.append(row)
    
    nav = []
    if page_num > 0:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"hpage_{page_num-1}"))
    nav.append(InlineKeyboardButton(f"Page {page_num+1}/{total_pages}", callback_data="none"))
    if page_num < total_pages - 1:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"hpage_{page_num+1}"))
    
    if nav:
        buttons.append(nav)
    return InlineKeyboardMarkup(buttons), len(mods)

@Hazel.Tele.on_message(filters.command("help"), sudo=True)
async def help_userbot(c: Client, m: Message):
    global BOT_INFO
    try:
        if not BOT_INFO["username"]:
             me = Hazel.Tele.bot.me or await Hazel.Tele.bot.get_me()
             BOT_INFO["username"] = str(me.username)
             
        bot_username = BOT_INFO["username"]
        results = await c.get_inline_bot_results(bot_username, "help")
        if results.results:
            await c.send_inline_bot_result(
                m.chat.id,
                results.query_id,
                results.results[0].id
            )
            if m.from_user and m.from_user.id == c.me.id:
                 try: await m.delete()
                 except: pass
        else:
            await m.reply("❌ **Error:** No results from the help bot. Ensure inline mode is ON.")
    
    except Exception as e:       
        error_msg = str(e)
        if 'CHAT_SEND_INLINE_FORBIDDEN' in error_msg:
             markup, count = get_help_markup(0)
             await m.reply(f"**HazelUB Help Menu**\n\nTotal Modules: {count}\n\n*Note: Inline is forbidden here.*", reply_markup=markup)
        elif "BOT_INLINE_DISABLED" in error_msg:
            await m.reply(f'❌ **Inline Disabled!**\nPlease enable inline mode for bot in @BotFather')
        else:
            logger.error(f"Error in help command: {e}")
            await m.reply(f"⚠️ **HazelUB Help Error**\n\n`{e}`")
            
        if m.from_user and m.from_user.id == c.me.id:
            try: await m.delete()
            except: pass

@Hazel.Tele.bot.on_inline_query(filters.regex("^help$"))
async def help_inline(c: Client, q: InlineQuery):
    markup, count = get_help_markup(0)
    if not markup:
        return await q.answer([
            InlineQueryResultArticle(
                title="No modules found",
                input_message_content=InputTextMessageContent("No modules with help found.")
            )
        ], cache_time=1)
    
    await q.answer([
        InlineQueryResultArticle(
            title="HazelUB Help Menu",
            description=f"Total Modules: {count}",
            input_message_content=InputTextMessageContent(f"**HazelUB Help Menu**\n\nTotal Modules: {count}"),
            reply_markup=markup
        )
    ], cache_time=1)

@Hazel.Tele.bot.on_callback_query(filters.regex(r"^hpage_(\d+)$"))
async def help_page_cb(c: Client, q: CallbackQuery):
    page_num = int(q.matches[0].group(1))
    markup, count = get_help_markup(page_num)
    await q.edit_message_text(
        f"**HazelUB Help Menu**\n\nTotal Modules: {count}",
        reply_markup=markup # type: ignore
    )

@Hazel.Tele.bot.on_callback_query(filters.regex(r"^hmod_(.*)_(\d+)$"))
async def help_mod_cb(c: Client, q: CallbackQuery):
    mod_name = q.matches[0].group(1)
    page_num = int(q.matches[0].group(2))
    mods = load_mods_help()
    help_text = mods.get(mod_name, "No help found.")
    
    buttons = [[InlineKeyboardButton("⬅️ Back", callback_data=f"hpage_{page_num}")]]
    await q.edit_message_text(
        f"**Module:** {mod_name}\n\n{help_text}",
        reply_markup=InlineKeyboardMarkup(buttons) # type: ignore
    )

@Hazel.Tele.bot.on_callback_query(filters.regex("none"))
async def none_cb(c, q):
    await q.answer()

MOD_NAME = "Help"
MOD_HELP = "Shows the bot help menu.\n\nUsage: `.help`"
