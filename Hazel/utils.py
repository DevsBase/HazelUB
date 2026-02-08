import sys, io, asyncio
from typing import Any
from pyrogram.client import Client
from pyrogram.types import Message
from Hazel import Tele, SQLClient

async def aexec(code: str, app: Client, m: Message) -> Any:
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    local_vars = {}
    
    try:
        exec(
            "async def __aexec_func(app, m, r, frm, chat_id, loop):\n"
            "    p = print\n"
            + "\n".join(f"    {l}" for l in code.split("\n")),
            globals(),
            local_vars,
        )
        func = local_vars["__aexec_func"]
        result = await func(
            app,
            m,
            m.reply_to_message,
            m.from_user,
            m.chat.id, # type: ignore
            asyncio.get_running_loop()
        )
    finally:
        sys.stdout = old_stdout

    output = buffer.getvalue()
    return output, result


