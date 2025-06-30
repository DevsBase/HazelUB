from pyrogram import Client
import asyncio
from Essentials.vars import __version__
import os

while (True):
  try: api_id = int(input('Enter your API_ID. (get from my.telegram.org): '))
  except: continue
  api_hash = input('Enter your API_HASH. (get from my.telegram.org): ')
  if len(api_hash) < 13: continue
  break

name = 'client'
client = Client(name, api_id=api_id, api_hash=api_hash, in_memory=True, device_model="HazelUB", system_version=f"HazelUB (v{__version__})")

async def main():
  await client.start()
  session = await client.export_session_string()
  print("SESSION STRING GENERATED\n")
  print(session)
    
asyncio.run(main())