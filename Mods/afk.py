from pyrogram.types import Message
from Hazel import Tele
import pyrogram

@Tele.on_message(pyrogram.filters.command("afk"))
async def afk_cmd(c: pyrogram.client.Client, m: Message):
        raise NotImplementedError

MOD_NAME = "AFK"
MOD_HELP = "> .afk - To set or unset afk. (Not work for sudoers)"