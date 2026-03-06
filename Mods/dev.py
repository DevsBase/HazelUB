from Hazel.enums import USABLE, WORKS
import asyncio
import os
import subprocess
from pathlib import Path

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message, InlineQuery

import restart
from Hazel import Tele
from Hazel.utils import aexec


@Tele.on_message(filters.command(["e", "eval"]), sudo=True)
@Tele.on_inline_query(filters.regex(r"^(e|eval)\s"), sudo=True)
async def evalFunc(c: Client, m: Message | InlineQuery):
    if not m or not m.from_user:
        return
    
    if Tele.getClientPrivilege(user_id=m.from_user.id) != "sudo":
        return await Tele.message(m).reply(
            "This client don't have `sudo` privillage. It is required to use this command."
        )

    cmd = m.text.split(None, 1) if isinstance(m, Message) else( # type: ignore
        m.query.split(None, 1)
    ) 

    client = Tele.getClientById(m.from_user.id) or Tele.bot

    if len(cmd) == 1:
        return await Tele.message(m).reply("No code provided.")
    if isinstance(m, Message):
        s = await m.reply("Evaluating...")
    try:
        result = await aexec(cmd[1], c, m)
    except Exception as e:
        result = (str(e), None)

    if len(result[0]) > 1999 or (result[1] and len(str(result[1])) > 1999):

        with open("eval.txt", "w", encoding="utf-8") as f:
            f.write(f"Output:\n{result[0]}\n\nResult:\n{result[1]}")

        if isinstance(m, Message):
            await m.reply_document(document="eval.txt")
        else:
            await Tele.inline(m).answer_text(title="Eval Result", text=f"You will rcv the result in @{client.me.username}.") # type: ignore
            await client.send_document(
                chat_id=m.from_user.id, document="eval.txt", caption="Eval Result"
            )
        await asyncio.to_thread(os.remove, "eval.txt")

    elif not result[1]:
        if isinstance(m, InlineQuery):
            return await Tele.inline(m).answer_text("Eval Result", f"Output:```python\n{result[0]}```")
        await Tele.message(s).edit(f"Output:```python\n{result[0]}```", business_connection_id=m.business_connection_id)
    elif not result[0]:
        if isinstance(m, InlineQuery):
            return await Tele.inline(m).answer_text("Eval Result", f"Result:```python\n{result[1]}```")
        await Tele.message(s).edit(f"Result:```python\n{result[1]}```", business_connection_id=m.business_connection_id)
    else:
        if isinstance(m, InlineQuery):
            return await Tele.inline(m).answer_text("Eval Result", f"Output:```python\n{result[0]}```\nResult:```python\n{result[1]}```")
        await Tele.message(s).edit(
            f"Output:```python\n{result[0]}```\nResult:```python\n{result[1]}```", business_connection_id=m.business_connection_id
        )


@Tele.on_message(filters.command("stop"), sudo=True)
@Tele.on_inline_query(filters.regex(r"^stop"), sudo=True)
async def stopFunc(c: Client, m: Message | InlineQuery):
    if not m or not m.from_user:
        return
    if Tele.getClientPrivilege(user_id=m.from_user.id) != "sudo":
        return await Tele.message(m).reply(
            "This client don't have `sudo` privillage. It is required to use this command."
        )
    await Tele.message(m).reply("Stopping HazelUB...")
    import os

    os._exit(0)


@Tele.on_message(filters.command("restart"), sudo=True)
@Tele.on_inline_query(filters.regex(r"^restart"), sudo=True)
async def restartFunc(c: Client, m: Message | InlineQuery):
    if not m or not m.from_user:
        return
    if Tele.getClientPrivilege(user_id=m.from_user.id) != "sudo":
        return await Tele.message(m).reply(
            "This client don't have `sudo` privillage. It is required to use this command."
        )
    await Tele.message(m).reply("Restarting...")
    restart.restart()


@Tele.on_message(filters.command("update"), sudo=True)
@Tele.on_inline_query(filters.regex(r"^update"), sudo=True)
async def updateFunc(c: Client, m: Message | InlineQuery):
    if not m or not m.from_user:
        return
    if Tele.getClientPrivilege(user_id=m.from_user.id) != "sudo":
        return await Tele.message(m).reply(
            "This client don't have `sudo` privillage. It is required to use this command."
        )
    s = await m.reply("Updating HazelUB...") if isinstance(m, Message) else None

    config_data, env_data = "", ""
    with open("config.py", "r") as f:
        config_data = f.read()

    if Path(".env").exists():
        with open(".env", "r") as f:
            env_data = f.read()

    result = subprocess.run(
        ["git", "pull", "origin", "main"], capture_output=True, text=True
    )

    try:
        with open("config.py", "w") as f:
            f.write(config_data)
        if env_data:
            with open(".env", "w") as f:
                f.write(env_data)
    except Exception as e:
        if isinstance(m, Message):
            await m.reply(f"Could not restore config files: {e}")

    if result.returncode != 0:
        return await Tele.message(m).reply(f"Update Failed:```bash\n{result.stderr}```")
    if "Already up to date." in result.stdout:
        return await Tele.message(m).reply("Already up to date.")

    msg = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"], capture_output=True, text=True, check=True
    ).stdout.strip()

    title, body = msg.split("\n\n", 1) if "\n\n" in msg else (msg, "")
    if isinstance(m, InlineQuery):
        return await Tele.inline(m).answer_text(
            "Update Successful",
            f"Commit message: {title}\nDescription: {body}\n\n`Restarting HazelUB...`"
        )
    elif s:
        await Tele.message(s).edit(
            f"**Update Successful:**```bash\n{result.stdout}```\n"
            f"**Update information:** \nCommit message: {title}\nDescription: {body}\n\n"
            "`Restarting HazelUB...`",
            business_connection_id=m.business_connection_id
        )
    restart.restart()


@Tele.on_message(filters.command(["logs", "log", "flogs"]), sudo=True)
async def logsFunc(c: Client, m: Message):
    if not m or not m.from_user:
        return
    if Tele.getClientPrivilege(user_id=m.from_user.id) != "sudo":
        return await m.reply(
            "This client don't have `sudo` privillage. It is required to use this command."
        )

    log_file = Path("log.txt")
    if not log_file.exists():
        return await m.reply("No logs found.")
    with open(log_file, "r") as f:
        log_data = f.read()
    if not "f" in m.command[0]:  # type: ignore
        logs = log_data[-4000:]
        await m.reply(f"Logs:```log\n{logs}```")
    else:
        await m.reply_document(document="log.txt")


@Tele.on_message(filters.command("sh"), sudo=True)
async def shellFunc(c: Client, m: Message):
    if not m or not m.from_user:
        return
    if Tele.getClientPrivilege(user_id=m.from_user.id) != "sudo":
        return await m.reply(
            "This client don't have `sudo` privillage. It is required to use this command."
        )

    cmd = m.text.split(None, 1)  # type: ignore
    if len(cmd) == 1:
        return await m.reply("No command provided.")

    import subprocess

    s = await m.reply("Executing...")
    result = await asyncio.to_thread(
        subprocess.run, cmd[1], shell=True, capture_output=True, text=True
    ) 

    if (
        result.stderr
        and len(result.stderr) > 1999
        or result.stdout
        and len(result.stdout) > 1999
    ):

        with open("shell.txt", "w", encoding="utf-8") as f:
            txt = result.stdout if result.returncode == 0 else result.stderr
            f.write(txt)

        await m.reply_document("shell.txt")
        return os.remove("shell.txt")

    if result.returncode != 0:
        return await Tele.message(s).edit(f"Command Failed:```bash\n{result.stderr}```", business_connection_id=m.business_connection_id)
    await Tele.message(s).edit(f"Command Output:```bash\n{result.stdout}```", business_connection_id=m.business_connection_id)


help = """**Usage:**
> .eval (code) - Evaluate python code.
> .sh (cmd) - Execute shell command.
> .restart - Restart HazelUB.
> .update - Update HazelUB.
> .logs - Get logs.
> .stop - Stop HazelUB.
"""
MOD_CONFIG = {
    "name": "Dev",
    "help": help,
    "works": WORKS.ALL,
    "usable": USABLE.OWNER & USABLE.SUDO
}