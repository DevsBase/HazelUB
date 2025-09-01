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