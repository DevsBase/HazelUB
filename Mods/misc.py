from Hazel import Tele
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message, InlineQuery, MessageEntity
from pyrogram.enums import MessageEntityType
from Hazel.enums import USABLE, WORKS

start_msg = """🔥 Hi, I'm Hazel Userbot!

⭐ Hazel is a powerful Telegram userbot built for automation and multi-account management. It supports multi-client sessions, Telegram Business integration, inline features, and sudo access for 🔒 trusted users.

⚡️ Fast, modular, and easy to extend with modules. 

🆘 Type /help to view available commands.
"""

entities: list[MessageEntity] = [
    MessageEntity(
        type=MessageEntityType.CUSTOM_EMOJI,
        offset=0,
        length=2,
        custom_emoji_id=4970107898341360413,
    ),
    MessageEntity(
        type=MessageEntityType.BOLD,
        offset=3,
        length=22,
    ),
    MessageEntity(
        type=MessageEntityType.CUSTOM_EMOJI,
        offset=27,
        length=1,
        custom_emoji_id=5267500801240092311,
    ),
    MessageEntity(
        type=MessageEntityType.CUSTOM_EMOJI,
        offset=220,
        length=2,
        custom_emoji_id=5197373721987260587,
    ),
    MessageEntity(
        type=MessageEntityType.CUSTOM_EMOJI,
        offset=239,
        length=2,
        custom_emoji_id=5363909133269481082,
    ),
    MessageEntity(
        type=MessageEntityType.CUSTOM_EMOJI,
        offset=292,
        length=2,
        custom_emoji_id=6301027265899661025,
    ),
    MessageEntity(
        type=MessageEntityType.BOT_COMMAND,
        offset=300,
        length=5,
    ),
    MessageEntity(
        type=MessageEntityType.BOLD,
        offset=300,
        length=5,
    ),
]



@Tele.on_message(filters.command("repo"), sudo=True)
@Tele.on_inline_query(filters.regex(r"^repo"), sudo=True)
async def repoFunc(c: Client, m: Message | InlineQuery):
    if isinstance(m, Message):
        if m.reply_to_message:
            m = m.reply_to_message
    await Tele.message(m).reply("https://github.com/DevsBase/HazelUB")

@Tele.bot.on_message(filters.command("start"))
async def start_cmd(c: Client, m: Message):
    if not m.command:
        return
    if len(m.command) > 1:
        if m.command[1] == "help_what_is_user":
            ...
    
    await m.reply(start_msg, entities=entities)

MOD_CONFIG = {
    "name": "Misc",
    "help": (
        "**Usage:**\n"
        "> .repo - to get the repo link."
    ),
    "works": WORKS.ALL,
    "usable": USABLE.ALL
}