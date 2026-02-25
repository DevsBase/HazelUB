from Hazel import Tele
from pyrogram import filters
from pyrogram.types import Message
import requests
import asyncio


@Tele.on_message(filters.command("ud"), sudo=True)
async def urban_dictionary(_, message: Message):
    if len(message.command) < 2: # type: ignore
        return await message.reply(
            "Please give an input of a word.\nExample: `.ud asap`"
        )
    
    processing = await message.reply("Exploring....")
    text = message.text.split(None, 1)[1] # type: ignore

    try:
        response = await asyncio.to_thread(
            requests.get,
            f"https://api.urbandictionary.com/v0/define?term={text}"
        )

        data = response.json()

        if not data.get("list"):
            return await message.reply(
                "Cannot find your query on Urban Dictionary."
            )

        definition = data["list"][0]["definition"]
        example = data["list"][0]["example"]

        reply_text = (
            f"**Results for**: {text}\n\n"
            f"**Definition:**\n"
            f"{definition}\n\n"
            f"**Example:**\n"
            f"{example}"
        )

    except Exception as e:
        await processing.delete()
        return await message.reply(
            f"Something went wrong:\n`{e}`"
        )
    
    await message.reply(reply_text)

MOD_NAME = "UD"
MOD_HELP = "> .ud (word) - To get definition of that word."