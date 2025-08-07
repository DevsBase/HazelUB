from Hazel import app, config, on_message, agent, HANDLER
from pyrogram import filters
import logging, traceback

chat_history = {}

SYSTEM_MESSAGE = ("system", "Your name is Hazel. You are a chat assistant and AI agent. Mainly you are Telegram userbot made by t.me/DevsBase. Use provided tools to help the user. And some times you have to act like user's girlfriend. You should satify them if they are horny. And you should never be like robotic. Respond to the user under 4,000 charactors (due telegram restrictions).")

@on_message(filters.command(['hazel', 'ai'], prefixes=HANDLER) & filters.me)
async def hazel_agent(client, m):
  if not config.GOOGLE_API_KEY or not agent:
    return await m.reply("There's no GOOGLE_API_KEY in env & config.json.")
  
  try:
    t = await m.reply("Thinking...")
    user_id = client.me.id
    history = chat_history.setdefault(user_id, [SYSTEM_MESSAGE])
    prompt = " ".join(m.command[1:])
    history.append(("user", prompt))
    chat_history[user_id] = [SYSTEM_MESSAGE] + history[-68:]
    response = await client.loop.run_in_executor(None, agent.invoke, {
      "messages": chat_history[user_id]
    })
    reply = response["messages"][-1].content
    chat_history[user_id].append(("assistant", reply))
    chat_history[user_id] = [SYSTEM_MESSAGE] + chat_history[user_id][-68:]
    await t.delete()
    await m.reply(reply)
  except Exception as e:
    logging.error(traceback.format_exc())
    return await m.reply(str(e))