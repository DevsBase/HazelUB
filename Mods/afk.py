from Hazel.enums import USABLE, WORKS
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
from Hazel import Tele, SQLClient
from MultiSessionManagement.decorators import _sudo_check
import time
from typing import Dict, Tuple

# Rate limiting cache
# Format: {client_id: {user_id: last_reply_timestamp}}
last_afk_reply: Dict[int, Dict[int, float]] = {}
AFK_REPLY_COOLDOWN = 60  # Reply at most once per minute per user

def format_duration(seconds: int) -> str:
    """Format duration in seconds to a human-readable string."""
    seconds = max(0, seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    
    parts = []
    if d > 0: parts.append(f"{d}d")
    if h > 0: parts.append(f"{h}h")
    if m > 0: parts.append(f"{m}m")
    if s > 0 or not parts: parts.append(f"{s}s")
    
    return " ".join(parts)


@Tele.on_message(filters.command(["afk"]) & filters.me)
async def afk_cmd(c: Client, m: Message):
    """Enable AFK mode."""
    if not c.me or not c.me.id or not SQLClient:
        return
    if m.from_user and m.from_user.id != c.me.id:
        return
        
    reason = None
    if m.command and len(m.command) > 1 and m.text:
        reason = m.text.split(None, 1)[1]
        
    await SQLClient.set_afk(c.me.id, True, reason)
    
    msg = "**I am now AFK.**"
    if reason:
        msg += f"\nReason: {reason}"
        
    await m.reply(msg)

@Tele.on_message(filters.command(["unafk"]) & filters.me)
async def unafk_cmd(c: Client, m: Message):
    """Disable AFK mode manually."""
    if not c.me or not c.me.id or not SQLClient:
        return
    if m.from_user and m.from_user.id != c.me.id:
        return
        
    is_afk, _, _ = await SQLClient.get_afk(c.me.id)
    if not is_afk:
        await m.reply("**I am not AFK.**")
        return
        
    await SQLClient.set_afk(c.me.id, False)
    await m.reply("**I am no longer AFK.**")

# Outgoing messages disable AFK automatically
@Tele.on_message(filters.outgoing & filters.me, group=2)
async def auto_unafk(c: Client, m: Message):
    """Automatically disable AFK on outgoing messages."""
    if not c.me or not c.me.id or not SQLClient:
        return
    # Sudoers sending messages from their accounts shouldn't unafk the main client
    # So we strictly check if the sender is the client itself
    if m.from_user and m.from_user.id != c.me.id:
        return
        
    is_afk, _, _ = await SQLClient.get_afk(c.me.id)
    if is_afk:
        await SQLClient.set_afk(c.me.id, False)
        try:
            msg = await m.reply("**I am no longer AFK.**")
            await __import__("asyncio").sleep(3)
            await msg.delete()
        except:
            pass

# Incoming PMs and mentions trigger AFK reply
@Tele.on_message((filters.private | filters.mentioned) & ~filters.me & ~filters.bot, group=1)
async def afk_reply(c: Client, m: Message):
    """Reply to PMs and mentions when AFK."""
    if not c.me or not c.me.id or not SQLClient:
        return
    if not m.from_user:
        return
        
    # Ignore Sudoers
    if await _sudo_check(None, c, m):
        return
        
    is_afk, reason, start_time = await SQLClient.get_afk(c.me.id)
    if not is_afk or start_time is None:
        return
        
    # Rate limiting check
    current_time = time.time()
    client_id = c.me.id
    user_id = m.from_user.id
    
    if client_id not in last_afk_reply:
        last_afk_reply[client_id] = {}
        
    if user_id in last_afk_reply[client_id]:
        if current_time - last_afk_reply[client_id][user_id] < AFK_REPLY_COOLDOWN:
            return
            
    last_afk_reply[client_id][user_id] = current_time
    
    # Calculate duration
    duration = int(current_time - start_time.timestamp())
    formatted_duration = format_duration(duration)
    
    reply_msg = "**I'm currently AFK.**\n"
    if reason:
        reply_msg += f"**Reason:** {reason}\n"
    reply_msg += f"**Since:** {formatted_duration}"
    
    await m.reply(reply_msg)


MOD_NAME = "AFK"
MOD_HELP = "> .afk [reason] - Enable AFK mode.\n> .unafk - Disable AFK mode manually."
MOD_WORKS = WORKS.ALL
MOD_USABLE = USABLE.OWNER
