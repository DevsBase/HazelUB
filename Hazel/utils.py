import sys, io, asyncio
from typing import Any
from pyrogram.client import Client
from pyrogram.types import Message
from Hazel import Tele, SQLClient

async def aexec(code: str, app: Client, m: Message) -> Any:
    """Asynchronously execute arbitrary Python code in an isolated scope.

    The *code* string is wrapped inside an async function and executed
    with a set of convenient local variables pre-injected:

    * ``app``     – the :class:`pyrogram.Client` instance.
    * ``m``       – the triggering :class:`pyrogram.types.Message`.
    * ``r``       – shortcut for ``m.reply_to_message``.
    * ``frm``     – shortcut for ``m.from_user``.
    * ``chat_id`` – the current chat ID.
    * ``loop``    – the running :class:`asyncio` event loop.
    * ``p``       – alias for the built-in ``print``.

    Any calls to ``print()`` inside the executed code are captured
    and returned as part of the output string.

    The literal ``r$4`` in *code* is replaced with ``return`` as a
    convenient shorthand.

    Args:
        code: The Python source code to execute.
        app: The active Pyrogram client.
        m: The message that triggered the execution.

    Returns:
        A tuple ``(output, result)`` where *output* is the captured
        stdout content and *result* is the return value of the
        executed code (if any).
    """
    code = code.replace('r$4', 'return')
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


