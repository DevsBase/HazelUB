from .. import *
from pyrogram import *
import random

@on_message(filters.command(['yes', 'no', 'ok', 'wtf', 'lol'], prefixes=HANDLER) & filters.reply & filters.me)
async def premium_reactions(client, m):
  cmd = m.command[0].lower()
  reactions = {
    "yes": [5413794461152978282, 5424972835095329742, 5352871660024246779],
    "no": [5413472879771658264, 5462882007451185227],
    "ok": [5787374221252365988, 5370846965741398160, 5415907099731304806],
    "wtf": [5359636439673882459],
    "lol": [5336824433845742459, 5353060840448727534, 6325330269624600344],
  }
  await m.delete()
  await m.reply_to_message.react(random.choice(reactions[cmd]))
  
@on_message(filters.command('echo', prefixes=HANDLER) & filters.reply & filters.me)
async def echo_func(client, m):
  await m.delete()
  await m.reply_to_message.copy(m.chat.id)

@on_message(filters.command(['dchat', 'delchat'], prefixes=HANDLER) & filters.private & filters.me)
async def delchat_func(client, m):
  await m.delete()
  await client.delete_chat_history(m.chat.id, revoke=True)
  
@on_message(filters.command("write", prefixes=HANDLER) & filters.me)
async def paper_write(_, message):
  if len(message.command) < 2:
    return await message.reply_text("I'll write. But what?.")
  m = await message.reply_text("Writing...")
  txt = (
    message.text.split(None, 1)[1]
    if len(message.command) < 3
    else message.text.split(None, 1)[1].replace(" ", "%20")
  )
  hand = "https://apis.xditya.me/write?text=" + txt
  await m.edit("Uploading...")
  await message.reply_photo(hand)
  await m.delete()  
  
@on_message(filters.command("repo", prefixes=HANDLER) & filters.user('me'))
async def repo(_, message):
  if message.reply_to_message:
    return await message.reply_to_message.reply("https://github.com/DevsBase/HazelUB", disable_web_page_preview=True)
  await message.reply("https://github.com/DevsBase/HazelUB", disable_web_page_preview=True)
  await message.delete()
  
MOD_NAME = "Misc"
MOD_HELP = """
.yes .no .ok .lol .wtf (reply) - To react to that message. premium required.
.echo (reply) - send the replied message without forward tag.
.write (text) - To write the text in a paper. 
.repo - To get Hazel github repo.
"""