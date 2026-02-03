from Hazel.utils import aexec
from Hazel import Tele, SQLClient
from pyrogram.client import Client
from pyrogram import filters
from pyrogram.types import Message

@Tele.on_message(filters.command(["e", "eval"]) & filters.me)
async def evalFunc(c: Client, m: Message):
    if c.privilege != 'sudo': # type: ignore
        return await m.reply("You don't have permission.")
    cmd = m.text.split(None, 1) # type: ignore
    if len(cmd) == 1:
        return await m.reply("No code provided.")
    try:
        result = await aexec(cmd[1], c, m)
    except Exception as e:
        result = (str(e), None)
    if not result[1]:
        await m.reply(f"Output:```python\n{result[0]}```")
    elif not result[0]:
        await m.reply(f"Result:```python\n{result[1]}```")
    else:
        await m.reply(f"Output:```python\n{result[0]}```\nResult:```python\n{result[1]}```")

@Tele.on_message(filters.command("stop") & filters.me)
async def stopFunc(c: Client, m: Message):
    if c.privilege != 'sudo': # type: ignore
        return await m.reply("You don't have permission.")
    await m.reply("Stopping HazelUB...")
    import os
    os._exit(0)

@Tele.on_message(filters.command("restart") & filters.me)
async def restartFunc(c: Client, m: Message):
    if c.privilege != 'sudo': # type: ignore
        return await m.reply("You don't have permission.")
    import restart
    await m.reply("Rerstarting...")
    restart.restart()