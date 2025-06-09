from .. import *
from pyrogram import filters
import asyncio

data = {}

@on_message(filters.command(['spam', 'sspam', 'slspam', 'dspam'], prefixes=HANDLER) & filters.me)
async def spam_func(app, message):
  global data
  m = message
  if app.me.id not in data: data[app.me.id]={}
  if m.command[0] == 'sspam':
    try:del data[app.me.id][m.chat.id]
    except:return await m.reply("no spams")
    return await m.reply("Spam stopped.")
  elif data[app.me.id].get(m.chat.id):
    return await m.reply("There's an ongoing spam going on this chat, so yeah you can't use multipul spams.")
  if message.reply_to_message:
    r = message.reply_to_message
    data[app.me.id][m.chat.id] = True
    while data[app.me.id].get(message.chat.id):
      x = await r.copy(m.chat.id)
      if m.command[0] == 'slspam' or m.command[0] == 'dspam':
        await asyncio.sleep(2.5)
        if m.command[0] == 'dspam': await x.delete()
      else: await asyncio.sleep(0.7)
  else:
    if len(message.text.split()) < 2:
      return await m.reply("You should reply to a message or give a text input.")
    text = message.text.split(None, 1)[1]
    data[app.me.id][m.chat.id] = True
    while data[app.me.id].get(message.chat.id):
      x = await app.send_message(m.chat.id, text)
      if m.command[0] == 'slspam' or m.command[0] == 'dspam':
        await asyncio.sleep(2.5)
        if m.command[0] == 'dspam': await x.delete()
      else: await asyncio.sleep(0.7)

MOD_NAME = "Spam"
MOD_HELP = """.spam <text> - To spam the text or reply to a message to spam it.
.sspam - To stop the ongoing spam.
.slspam - Slow spam 2.5 sec delay for each.
.dspam - Same as slspam or (slow spam), but it would delete the spam message. used in chatfight bot's rank boosting.
"""