from typing import List, Optional
import asyncio

from Hazel import Tele
import pyrogram
from pyrogram.types import Message
from duckduckgo_search import DDGS


@Tele.on_message(pyrogram.filters.command("search"), sudo=True)
async def search(_, message: Message) -> None:
    command: Optional[List[str]] = message.command

    if not command or len(command) < 2:
        await message.reply("Okay, I'll search — but what?")
        return

    query: str = " ".join(command[1:])
    loading: Message = await message.reply("`Loading...`")

    try:
        def run_search() -> List[str]:
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=10)
                return [r["href"] for r in results]

        results: List[str] = await asyncio.to_thread(run_search)

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
MOD_HELP: str = ".search <query> - search web pages links."