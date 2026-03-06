from Hazel.enums import USABLE, WORKS
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message, InlineQuery
from Hazel import Tele
import asyncio
import wikipediaapi

wiki = wikipediaapi.Wikipedia(
    user_agent="HazelUB/1.0 (https://github.com/DevsBase/HazelUB)",
    language='en',
    extract_format=wikipediaapi.ExtractFormat.WIKI
)

@Tele.on_message(filters.command(["wiki", "wikipedia"]), sudo=True)
@Tele.on_inline_query(filters.regex(r"^(wiki|wikipedia)\s"), sudo=True)
async def wiki_cmd(c: Client, m: Message | InlineQuery):
    if not m or not m.from_user:
        return

    if isinstance(m, Message):
        if not m.text:
            return
        cmd = m.text.split(None, 1)
        query = cmd[1] if len(cmd) > 1 else None
        status = await m.reply("Searching...")
    else:
        cmd = m.query.split(None, 1)
        query = cmd[1] if len(cmd) > 1 else None

    if not query:
        msg = "Usage: `.wiki <query>`"
        if isinstance(m, Message):
            return await Tele.message(status).edit(msg, business_connection_id=m.business_connection_id)
        return await Tele.message(m).reply(msg, title="Wiki Error")

    try:
        page = await asyncio.to_thread(wiki.page, query)

        if not page.exists():
            res = f"No results for: **{query}**"
            if isinstance(m, Message):
                return await Tele.message(status).edit(res, business_connection_id=m.business_connection_id)
            return await Tele.message(m).reply(res, title="Not Found")

        summary = page.summary[:1000]
        response_text = (
            f"**{page.title}**\n\n"
            f"{summary}...\n\n"
            f"[Read More]({page.fullurl})"
        )

        if isinstance(m, Message):
            await Tele.message(status).edit(
                response_text,
                disable_web_page_preview=False,
                business_connection_id=m.business_connection_id
            )
        else:
            await Tele.message(m).reply(response_text, title=page.title)

    except Exception as e:
        err = f"Error: `{e}`"
        if isinstance(m, Message):
            await Tele.message(status).edit(err, business_connection_id=m.business_connection_id)
        else:
            await Tele.message(m).reply(err, title="Wiki Error")

help_text = """**Usage:**
> .wiki (query) - Search Wikipedia.
"""

MOD_CONFIG = {
    "name": "Wikipedia",
    "help": help_text,
    "works": WORKS.ALL,
    "usable": USABLE.ALL,
    "requires": {
        "wikipedia-api": ">=0.6.0"
    }
}