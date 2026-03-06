from Hazel.enums import USABLE, WORKS
import asyncio

import requests
from pyrogram import filters
from pyrogram.types import Message, InlineQuery

from Hazel import Tele

async def search_urban_dictionary(term: str) -> dict:
    response = await asyncio.to_thread(
        requests.get,
        f"https://api.urbandictionary.com/v0/define?term={term}"
    )
    return response.json()


@Tele.on_message(
    filters.regex(r"^ud\s+(\w+)") | filters.command("ud"),
    sudo=True,
    inline=True
)
async def urban_dictionary(_, message: Message | InlineQuery):
    if isinstance(message, InlineQuery):
        term = message.query.split(None, 1)[1] if len(message.query.split(None, 1)) > 1 else None
        if not term:
            return await Tele.inline(message).answer_text(
                title="Urban Dictionary",
                description="Please provide a term to search for.",
                text="Please provide a term to search for.\nExample: `> ud girl`"
            )
        return
    else:
        if message.command and len(message.command) < 2:
            return await message.reply(
                "Please give an input of a word.\nExample: `.ud asap`"
            )
    
        processing = await message.reply("Exploring....")
        term = message.text.split(None, 1)[1] # type: ignore

    try:
        data = await search_urban_dictionary(term)

        if not data.get("list"):
            if isinstance(message, InlineQuery):
                return await Tele.inline(message).answer_text(
                    title="Urban Dictionary",
                    description="Cannot find your query on Urban Dictionary.",
                    text="Cannot find your query on Urban Dictionary."
                )
            return await Tele.message(processing).edit(
                "Cannot find your query on Urban Dictionary.",
                business_connection_id=message.business_connection_id
            )

        definition = data["list"][0]["definition"]
        example = data["list"][0]["example"]

        reply_text = (
            f"**Results for**: {term}\n\n"
            f"**Definition:**\n"
            f"{definition}\n\n"
            f"**Example:**\n"
            f"{example}"
        )

    except Exception as e:
        if isinstance(message, InlineQuery):
            await Tele.inline(message).answer_text(
                title="Urban Dictionary",
                description=f"Something went wrong: {e}",
                text=f"Something went wrong:\n`{e}`"
            )
            return
        await Tele.message(processing).delete(business_connection_id=message.business_connection_id)
        return await message.reply(
            f"Something went wrong:\n`{e}`"
        )
    if isinstance(message, InlineQuery):
        await Tele.inline(message).answer_text(
            title=f"Urban Dictionary: {term}",
            text=reply_text
        )
    await Tele.message(processing).delete(business_connection_id=message.business_connection_id)
    await message.reply(reply_text)

MOD_CONFIG = {
    "name": "Urban Dictionary",
    "help": "> .ud (word) - To get definition of that word.",
    "works": WORKS.ALL,
    "usable": USABLE.ALL
}
