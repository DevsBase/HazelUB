from pyrogram import Client
import asyncio

client = Client("client")

async def main():
  await client.start()
  
asyncio.run(main())