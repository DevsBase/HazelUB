from Hazel.enums import USABLE, WORKS
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from Hazel import Tele
from Hazel.Platforms.Telegram.decorators import sudo_check

SETTINGS_BUTTONS = [
    [
        InlineKeyboardButton("idk")
    ],
    [
        InlineKeyboardButton("Stop", "stop"),
        InlineKeyboardButton("Restart", "restart")
    ],
    [
        InlineKeyboardButton("HazelUB")
    ]
]
@Tele.bot.on_callback_query(filters.regex(r"^settings") & filters.create(sudo_check))
async def settings_cb(c: Client, q: CallbackQuery):
    await q.edit_message_text("Settings", reply_markup=InlineKeyboardMarkup(SETTINGS_BUTTONS))