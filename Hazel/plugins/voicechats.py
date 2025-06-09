from .. import *
from pyrogram import *
from MultiSessionManagement import *

@on_message(filters.command(['joinvc','jv'], prefixes=HANDLER)&filters.me&filters.group)
async def joinvc(c,m):
  await m.delete()
  pytgcalls_client = clients_data[c.me.id]["pytgcalls_client"]
  await pytgcalls_client.play(m.chat.id)
  
@on_message(filters.command(['leavevc','lv'], prefixes=HANDLER)&filters.me&filters.group)
async def leavevc(c,m):
  await m.delete()
  pytgcalls_client = clients_data[c.me.id]["pytgcalls_client"]
  try: await pytgcalls_client.leave_call(m.chat.id)
  except:
    await pytgcalls_client.play(m.chat.id)
    await pytgcalls_client.leave_call(m.chat.id)
    