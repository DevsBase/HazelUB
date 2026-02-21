from Hazel import Tele, SQLClient
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import (
    Message, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent
)
import time
import logging

logger = logging.getLogger("Mods.afk")

def get_readable_time(seconds: int) -> str:
    # Weeks support for the user's requested style
    weeks, seconds = divmod(seconds, 604800)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    
    parts = []
    if weeks: parts.append(f"{int(weeks)}w")
    if days: parts.append(f"{int(days)}d")
    if hours: parts.append(f"{int(hours)}h")
    if minutes: parts.append(f"{int(minutes)}m")
    parts.append(f"{int(seconds)}s")
    
    return ":".join(parts)

@Tele.on_message(filters.command("afk") & filters.me)
async def afk_cmd(c: Client, m: Message):
    reason = "Away from keyboard"
    if len(m.command) > 1:
        reason = m.text.split(None, 1)[1]
    
    await SQLClient.set_afk(c.me.id, reason)
    
    bot_username = (await Tele.bot.get_me()).username
    results = await c.get_inline_bot_results(bot_username, f"afk_set {reason}")
    if results.results:
        await c.send_inline_bot_result(
            m.chat.id,
            results.query_id,
            results.results[0].id
        )
        await m.delete()

# --- AFK Cancellation Listener ---
@Tele.on_message(filters.me & ~filters.command(["afk", "ping", "uptime"]))
async def afk_stop_listener(c: Client, m: Message):
    afk_data = await SQLClient.get_afk(c.me.id)
    if afk_data:
        duration = get_readable_time(int(time.time() - afk_data["time"]))
        await SQLClient.remove_afk(c.me.id)
        await m.reply(f"✅ **I'm back!**\nI was AFK for `{duration}`.")

# --- AFK Mention/Reply Listener ---
@Tele.on_message(filters.incoming & ~filters.me)
async def afk_mention_listener(c: Client, m: Message):
    # We check if:
    # 1. The message mentions the user (c.me.id)
    # 2. The message is a reply to the user (c.me.id)
    
    is_mentioned = False
    if m.mentioned:
         is_mentioned = True
    elif m.reply_to_message and m.reply_to_message.from_user and m.reply_to_message.from_user.id == c.me.id:
         is_mentioned = True
         
    if not is_mentioned:
        return

    afk_data = await SQLClient.get_afk(c.me.id)
    if afk_data:
        duration = get_readable_time(int(time.time() - afk_data["time"]))
        reason = afk_data["reason"]
        await m.reply(
            f"👤 **{c.me.first_name} is AFK.**\n"
            f"📝 **Reason:** `{reason}`\n"
            f"🕒 **Away for:** `{duration}`"
        )

# --- Inline Handlers ---

@Tele.bot.on_inline_query(filters.regex(r"^afk_set (.*)"))
async def afk_inline(c: Client, q: InlineQuery):
    reason = q.matches[0].group(1)
    await q.answer([
        InlineQueryResultArticle(
            title="Go AFK",
            description=f"Reason: {reason}",
            input_message_content=InputTextMessageContent(
                f"💤 **I am now AFK.**\n"
                f"📝 **Reason:** `{reason}`"
            )
        )
    ], cache_time=0)

MOD_NAME = "AFK"
MOD_HELP = "Set yourself AFK.\n\nUsage:\n> .afk [reason] - Go AFK. Any message you send will turn it off."
