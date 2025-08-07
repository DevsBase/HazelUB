from pyrogram import Client
import asyncio
import os

while (True):
  try: api_id = int(input('Enter your API_ID. (get from my.telegram.org): '))
  except: continue
  break
while (True):
  api_hash = input('Enter your API_HASH. (get from my.telegram.org): ')
  if len(api_hash) < 13: continue
  break

name = 'client'
client = Client(name, api_id=api_id, api_hash=api_hash, in_memory=True, device_model="HazelUB")

async def main():
  await client.start()
  session = await client.export_session_string()
  text = f"SESSION STRING GENERATED\n\n{session}"
  await client.send_message('me', text)
  print(text)
    
asyncio.run(main())