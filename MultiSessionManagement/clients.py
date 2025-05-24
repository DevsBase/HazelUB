import logging
from art import *
from pyrogram import *
from clear import clear
import asyncio
from pytgcalls import PyTgCalls
import logging

log = logging.getLogger(__name__)
clients, clients_data = [],{}
TgCallsClients = []

def add_client(client):
  global clients,TgCallsClients
  if client not in clients:
    clients.append(client)
    client.pytgcalls = PyTgCalls(client)
    TgCallsClients.append(client.pytgcalls)

async def start_all():
  global clients_data,TgCallsClients
  from Hazel import bot,nexbot
  await bot.start()
  await nexbot.start()
  for client in clients:
    privilege = f"{'sudo' if client == clients[0] else 'user'}"
    await client.start()
    await client.pytgcalls.start()
    client.privilege = privilege      
    clients_data[client.me.id] = {"client": client, "StreamingChats": {}, "pytgcalls_client": client.pytgcalls,"privilege": privilege}
  from Essentials.vars import AutoJoinChats, Support
  for app in clients:
    for i in AutoJoinChats:
      try: await app.join_chat(i)
      except: pass
  z,x,c=clear(),print(text2art("HazelUB"), end=""),logging.info("You're all set!")
  try: await clients[0].send_message(Support,"Up!")
  except: pass
  from personal.UpdateWaitingDays import UpdateWaitingDays
  asyncio.create_task(UpdateWaitingDays(clients[0]))
  await idle()