from .. import *
from pyrogram import *
import base64
import aiohttp

@on_message(filters.command(["tm", "imgur"], prefixes=HANDLER) & filters.user('me'))
async def imgur(app, message):
  msg = await message.reply("`Uploading...`")
  if message.reply_to_message and (message.reply_to_message.photo or message.reply_to_message.animation):
    file_path = await message.reply_to_message.download()
    with open(file_path, "rb") as file:
      base64_data = base64.b64encode(file.read()).decode()
    url = "https://api.imgur.com/3/image"
    headers = {"Authorization": "Client-ID a10ad04550b0648"}
    async with aiohttp.ClientSession() as session:
      async with session.post(url, headers=headers, data={"image": base64_data}) as response:
        result = await response.json()
        try:await msg.edit(f"""**Your link has been generated**: {result["data"]["link"]}""", disable_web_page_preview=True)
        except Exception as e:
          await msg.edit(f"Error: {e}. Result from API: {result}")
  else:
    await msg.edit("Please reply to a photo or animation (GIF) to upload to Imgur.")
    
MOD_NAME = "Imgur"
MOD_HELP = ".imgur (reply to a photo/animation) - To get its imgur link. (imgur.com)"