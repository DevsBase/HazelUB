from Hazel.utils import aexec
from Hazel import Tele, SQLClient
from pyrogram.client import Client
from pyrogram import filters
from pyrogram.types import Message
from pathlib import Path

@Tele.on_message(filters.command(["e", "eval"]) & filters.me)
async def evalFunc(c: Client, m: Message):
    if c.privilege != 'sudo': # type: ignore
        return await m.reply("You don't have permission.")
    cmd = m.text.split(None, 1) # type: ignore
    if len(cmd) == 1:
        return await m.reply("No code provided.")
    s = await m.reply("Evaluating...")
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
    await s.delete()

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

@Tele.on_message(filters.command("update") & filters.me)
async def updateFunc(c: Client, m: Message):
    if c.privilege != 'sudo': # type: ignore
        return await m.reply("You don't have permission.")
    import subprocess
    s = await m.reply("Updating HazelUB...")
    
    config_data = ""
    with open("config.py", "r") as f:
        config_data = f.read()
    
    env_data = ""
    if Path(".env").exists():
        with open(".env", "r") as f:
            env_data = f.read()
    
    result = subprocess.run(
        ["git", "pull", "origin", "main"],
        capture_output=True,
        text=True
    )
    await s.delete()
    try:
        with open("config.py", "w") as f:
            f.write(config_data)
        if env_data:
            with open(".env", "w") as f:
                f.write(env_data)
    except Exception as e:
        await m.reply(f"Could not restore config files: {e}")
    
    if result.returncode != 0:
        return await m.reply(f"Update Failed:```bash\n{result.stderr}```")
    if "Already up to date." in result.stdout:
        return await m.reply("Already up to date.")
    await m.reply(f"Update Successful:```bash\n{result.stdout}```\nRestarting...")
    import restart
    restart.restart()

@Tele.on_message(filters.command("logs") & filters.me)
async def logsFunc(c: Client, m: Message):
    if c.privilege != 'sudo': # type: ignore
        return await m.reply("You don't have permission.")
    log_file = Path("log.txt")
    if not log_file.exists():
        return await m.reply("No logs found.")
    with open(log_file, "r") as f:
        log_data = f.read()
    if len(log_data) < 4096:
        return await m.reply(f"Logs:```log\n{log_data}```")
    await m.reply_document(document=str(log_file))