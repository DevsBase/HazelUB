from pyrogram import Client
import asyncio

while (True):
  try: api_id = int(input('Enter your API_ID. (get from my.telegram.org): '))
  except: continue
  api_hash = input('Enter your API_HASH. (get from my.telegram.org): ')
  if len(api_hash) < 13: continue
  break

client = Client("client", api_id=api_id, api_hash=api_hash)

async def main():
  await client.start()
  
asyncio.run(main())