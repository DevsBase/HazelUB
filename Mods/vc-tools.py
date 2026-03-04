from Hazel import Tele
from Hazel.enums import USABLE, WORKS
import pyrogram

@Tele.on_message(pyrogram.filters.command(['joinvc', 'jv', 'leavevc', 'lv']) & pyrogram.filters.group, sudo=True)
async def joinvc(c: pyrogram.client.Client, m: pyrogram.types.Message):
    tgcalls = Tele.getClientPyTgCalls(c)
    chat = m.chat.id or 0 # type: ignore
    cmd = m.command[0].lower() or 'jv' # type: ignore
    if not tgcalls:
      return
    await m.delete()
    if cmd in ['lv', 'leavevc']:
        await tgcalls.play(chat)
        await tgcalls.leave_call(chat)
    else:
        await tgcalls.play(chat)
        await tgcalls.mute(chat)
  
"""**Usage:**
> .joinvc / .jv - to join in a vc.
> .leavevc / .lv - to leave in a vc.

Only works on groups
"""

MOD_CONFIG = {
    "name": "VC Tools",
    "help": __doc__,
    "works": WORKS.GROUP,
    "usable": USABLE.OWNER & USABLE.SUDO
}