from Hazel import *
from pyrogram import *

@on_message(filters.command('afk', prefixes=HANDLER) & filters.me)
async def set_afk(_, m):
  uid = m.from_user.id
  is_afk = await db.is_afk(uid)
  if is_afk: await m.reply("You've already in afk.")
  await db.set_afk(uid)
  await m.reply("Set!")
  
@on_message(filters.private, group=100)
async def handle_afk(c, m):
  uid = c.me.id
  is_afk = await db.is_afk(uid)
  await m.reply("I'm currently unavalable.")