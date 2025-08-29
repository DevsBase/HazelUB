from requests import get
from .. import *
from pyrogram import *
import asyncio
import aiofiles.os

@on_message(filters.command(["github", "git"], prefixes=HANDLER) & filters.me)
async def git(app, message):
  if len(message.command) < 2:
    return await message.reply_text("Where username?")
  user = message.text.split(None, 1)[1]
  res = get(f"https://api.github.com/users/{user}").json()
  data = f"""
**Name:** {res['name']}
**Username:** `{res['login']}`
**Link:** [{res['login']}]({res['html_url']})
**Bio:** `{res['bio']}`
**Company:** {res['company']}
**Blog:** {res['blog']}
**Location:** {res['location']}
**Repos:** `{res['public_repos']}`
**Followers:** `{res['followers']}`
**Following:** `{res['following']}`
**Account created:** `{res['created_at']}`
"""
  with open(f"{user}.jpg", "wb") as f:
    kek = get(res["avatar_url"]).content
    f.write(kek)
  await message.reply_photo(f"{user}.jpg", caption=data)
  await aiofiles.os.remove(f"{user}.jpg")
  
MOD_NAME = 'Git'
MOD_HELP = ".git <github username> - To get information of that github account"