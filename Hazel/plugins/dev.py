import io
import sys
import traceback
from .. import *
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
import contextlib
import asyncio
import aiofiles
from MultiSessionManagement import *

async def aexec(code, client, msg):
  m, from_user, r = msg, msg.from_user, msg.reply_to_message
  local_vars = {}
  exec(
    "async def __otazuki_run(client, message, m, r, frm, chat_id): "
    + "\n p = print"
    + "\n here = m.chat.id"
    + "".join(f"\n {l_}" for l_ in code.split("\n")),
    globals(),
    local_vars,
  )
  func = local_vars.get("__otazuki_run")
  if not func:
    raise KeyError("__otazuki_run not defined")
  return await func(client, msg, m, r, from_user, m.chat.id)

@on_message(filters.command(["e", "eval"],prefixes=HANDLER) & filters.me)
async def eval_func(c, msg):
  if (clients_data[c.me.id].get('privilege')!='sudo'):
    return await msg.reply("You don't have permisson.")
  cmd = msg.text.split(None, 1)
  if len(cmd) == 1:
    return await msg.reply("ᴄᴏᴅᴇ ɴᴏᴛ ғᴏᴜɴᴅ!")
  message = await msg.reply("ʀᴜɴɴɪɴɢ...")
  stdout, stderr, exc = None, None, None
  with contextlib.redirect_stdout(io.StringIO()) as redr_opu, contextlib.redirect_stderr(io.StringIO()) as redr_err:
    try:
      x = await aexec(cmd[1], c, msg)
    except Exception:
      exc = traceback.format_exc()
    stdout, stderr = redr_opu.getvalue(), redr_err.getvalue()
  output = exc or stderr or stdout or x or "ɴᴏ ᴏᴜᴛᴘᴜᴛ"
  output_text = f"📒 ᴏᴜᴛᴘᴜᴛ:\n<pre>{output}</pre>"
  if len(output_text) >= 4000:
    import aiofiles
    async with aiofiles.open("result.txt", mode='w') as f:
      await f.write(output)
    await message.reply_document('result.txt')
    import aiofiles.os
    try: await aiofiles.os.remove("result.txt")
    except: pass
  else:
    await message.reply(output_text, parse_mode=ParseMode.HTML)
  await message.delete()

@on_message(filters.command(["sh", "shell"], prefixes=HANDLER) & filters.me)
async def shell(c, message):
  if (clients_data[c.me.id].get('privilege')!='sudo'):
    return await msg.reply("You don't have permisson.")
  if len(message.command) < 2:
    return await message.reply("Please enter a command to run!")
  code = message.text.split(None, 1)[1]
  message_text = await message.reply_text("`Processing...`")
  try:
    process = await asyncio.create_subprocess_shell(
      code,
      stdout=asyncio.subprocess.PIPE,
      stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    output = (stdout.decode() + stderr.decode()).strip()
    if not output:
      output = "ɴᴏ ᴏᴜᴛᴘᴜᴛ"
    if len(output) > 4096:
      async with aiofiles.open("shell.txt", mode='w') as x:
        await x.write(output)
      await message.reply_document("shell.txt")
      await message_text.delete()
    else:
      await message_text.edit(f"**Output**:\n`{output}`")
  except Exception as e:
    await message_text.edit(f"**Error**:\n`{str(e)}`")    

@on_message(filters.command(["log", "logs", "flog", "flogs"], prefixes=HANDLER) & filters.me)
async def log(c, m):
  if (clients_data[c.me.id].get('privilege')!='sudo'):
    return await m.reply("You don't have permisson.")
  x = await m.reply("Processing...")
  async with aiofiles.open("log.txt", mode="r") as l:
    xx = await l.read()
  if len(xx) > 4000 and 'f' in m.command[0]:
    await m.reply_document("log.txt")
  else: await m.reply(f"<pre>{xx[-2000:]}</pre>", parse_mode=ParseMode.HTML)
  await x.delete()

@on_message(filters.command("restart", prefixes=HANDLER) & filters.me)
async def restart_func(c, message):
  if (clients_data[c.me.id].get('privilege')!='sudo'):
    return await message.reply("You don't have permisson.")  
  await message.reply("Restarting...")
  from restart import restart
  restart()