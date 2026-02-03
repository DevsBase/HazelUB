from .. import *
from pyrogram import *

@on_message(filters.command(['d','del','delete'], prefixes=HANDLER) & filters.me)
async def d(_,m):
  