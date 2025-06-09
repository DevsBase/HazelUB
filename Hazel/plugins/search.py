from .. import *
from pyrogram import *
from googlesearch import search as g_search

@on_message(filters.command("search", prefixes=HANDLER) & filters.me)
async def search(_, message):
  if len(message.text.split()) < 2:
    return await message.reply("Okay, i'll search but what?.")
  MSG = await message.reply("`Loading...`")
  try:
    links = "\n".join([f"{i+1}. {j}" for i, j in enumerate(g_search(" ".join(message.command[1:]), num=10, stop=10, pause=2))])
    await MSG.edit(f"**Results:**\n\n{links}", disable_web_page_preview=True)
  except Exception as e:
    await MSG.edit(f"Error: {e}")
    
MOD_NAME = "Search"
MOD_HELP = ".search - search web pages links from google."