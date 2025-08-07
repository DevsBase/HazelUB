from Hazel import app, config, on_message, agent, HANDLER
from langchain_google_genai import ChatGoogleGenerativeAI
from pyrogram import filters
import logging
import traceback

chat_history = []

@on_message(filters.command('hazel', prefixes=HANDLER) & filters.me)
async def hazel_agent(client, m):
  if not config.GOOGLE_API_KEY or not agent:
    return await m.reply("There's no GOOGLE_API_KEY in env & config.json.")
  try:
    t = await m.reply("Thinking...")
    promt = m.text.split(None, 1)
    response = await client.loop.run_in_executor(None, agent.invoke, {"messages": [("user", promt)]})  
    await t.delete()
    await m.reply(response["messages"][-1].content)
  except Exception as e:
    logging.error(traceback.format_exc())
    return await m.reply(e)