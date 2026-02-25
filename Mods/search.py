from typing import List, Optional, Union
import asyncio

from Hazel import Tele
import pyrogram
from pyrogram.types import Message
from googlesearch import search as gsearch
from googlesearch import SearchResult


@Tele.on_message(pyrogram.filters.command("search"), sudo=True)
async def search(_, message: Message) -> None:

    command: Optional[List[str]] = message.command

    if not command or len(command) < 2:
        await message.reply("Okay, I'll search — but what?")
        return

    query: str = " ".join(command[1:])
    loading: Message = await message.reply("`Loading...`")

    try:
        raw_results: List[Union[SearchResult, str]] = await asyncio.to_thread(
            lambda: list(gsearch(query, num_results=10))
        )

        # Normalize everything into plain URLs
        results: List[str] = [
            r.url if isinstance(r, SearchResult) else str(r)
            for r in raw_results
        ]

        if not results:
            await loading.edit("No results found.")
            return

        links: str = "\n".join(
            f"{i + 1}. {url}"
            for i, url in enumerate(results)
        )

        await loading.edit(
            f"**Results:**\n\n{links}",
            disable_web_page_preview=True
        )

    except Exception as e:
        await loading.edit(f"Error: {e}")


MOD_NAME: str = "Search"
MOD_HELP: str = ".search <query> - search web pages links from Google."