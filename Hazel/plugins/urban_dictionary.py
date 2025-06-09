from .. import *
from pyrogram import filters
import requests

@on_message(filters.command("ud",prefixes=HANDLER) & filters.me)
async def urban_dictionary(_, message):
  if len(message.command) < 2:
    return await message.reply("Please give an input of a word.\nExample: `.ud asap`")         
  text = message.text.split(None, 1)[1]
  try:
    results = requests.get(
      f'https://api.urbandictionary.com/v0/define?term={text}').json()
    reply_text = f"""
**Results for**: {text}

**Defination**:
{results["list"][0]["definition"]}\n
**Example:**
{results["list"][0]["example"]}
"""
  except Exception as e:
    if str(e) == "list index out of range":
      return await message.reply("Cannot find your query on Urban dictionary.")
    return await message.reply(f"Somthing wrong Happens:\n`{e}`")
  mm = await message.reply("Exploring....")
  await message.reply(reply_text)
  await mm.delete()

MOD_NAME = "UD"
MOD_HELP = ".ud <word> - To get definition of that word."