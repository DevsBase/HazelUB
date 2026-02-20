from typing import Dict, List, Optional, TypedDict, Union
import logging
import asyncio
import os

from pyrogram.client import Client
from pyrogram import filters
from pyrogram.types import (
    Message, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    CallbackQuery,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Chat
)
from pyrogram.enums import ButtonStyle
from pyrogram.errors import BadRequest
from pytgcalls import filters as call_filters
from pytgcalls import PyTgCalls
from pytgcalls.types import Update

from Hazel import Tele

# --- Logging Setup ---
logger = logging.getLogger("Mods.Music")

# --- Types ---
class SongDict(TypedDict):
    path: str
    title: str
    performer: str
    duration: int
    file_name: str

class SessionData(TypedDict):
    queue: List[SongDict]
    loop: int  # 0: Off, 1: Track, 2: Queue
    current: Optional[SongDict]
    client: Client
    is_paused: bool
    ui_msg_id: Optional[int]

# --- Global State ---
streaming_chats: Dict[int, SessionData] = {}

# --- Helper Functions ---
def get_duration_str(seconds: int) -> str:
    """Converts seconds to MM:SS format."""
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"

def get_track_text(song: SongDict, status: str = "Now Playing", loop_mode: int = 0) -> str:
    """Generates the formatted text for a track."""
    modes = {0: "Off", 1: "Track", 2: "Queue"}
    return (
        f"**{status}**\n\n"
        f"**Title:** `{song['title']}`\n"
        f"**Artist:** `{song['performer']}`\n"
        f"**Duration:** `{get_duration_str(song['duration'])}`\n"
        f"**Loop Mode:** `{modes.get(loop_mode, 'Off')}`"
    )

def get_music_keyboard(chat_id: int, loop_mode: int, is_paused: bool = False) -> InlineKeyboardMarkup:
    """Creates the control keyboard for the music player using standard emojis."""
    
    pause_resume_text = "▶️ Resume" if is_paused else "⏸ Pause"
    pause_resume_cb = f"mus_resume_{chat_id}" if is_paused else f"mus_pause_{chat_id}"
    
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(pause_resume_text, callback_data=pause_resume_cb),
            InlineKeyboardButton("⏭ Skip", callback_data=f"mus_skip_{chat_id}"),
        ],
        [
            InlineKeyboardButton("🔁 Loop", callback_data=f"mus_loop_{chat_id}"),
            InlineKeyboardButton("📜 Queue", callback_data=f"mus_queue_{chat_id}"),
            InlineKeyboardButton("🛑 Stop", callback_data=f"mus_stop_{chat_id}"),
        ],
        [
            InlineKeyboardButton("Close Player", callback_data=f"mus_close_{chat_id}", style=ButtonStyle.DANGER)
        ]
    ])

async def is_authorized(client: Client, chat_id: int, user_id: int) -> bool:
    """Checks if a user is authorized to control the music (sudo or admin)."""
    # 1. Check if the user is one of our own accounts (Sudo)
    for ub_client in Tele._allClients:
        if ub_client.me and ub_client.me.id == user_id:
            return True
    
    # 2. Check if the user is a chat administrator
    try:
        return await Tele.is_admin(client, chat_id, user_id)
    except Exception as e:
        logger.debug(f"Admin check failed: {e}")
        return False

async def send_track_ui(chat_id: int, song: SongDict, status: str = "Now Playing", force_new: bool = True):
    """Sends the track UI, attempting to edit existing if force_new is False."""
    data = streaming_chats.get(chat_id)
    if not data:
        return
    
    loop_mode = data["loop"]
    is_paused = data.get("is_paused", False)
    text = get_track_text(song, status, loop_mode)
    client = data["client"]

    # Try to edit existing message if not forced to send new
    ui_msg_id = data.get("ui_msg_id")
    if not force_new and ui_msg_id:
        try:
            await client.edit_message_text(
                chat_id,
                ui_msg_id,
                text,
                reply_markup=get_music_keyboard(chat_id, loop_mode, is_paused)
            )
            return
        except Exception as e:
            logger.debug(f"Edit failed (falling back to new message): {e}")

    # Delete previous UI if exists
    if ui_msg_id:
        try:
            await client.delete_messages(chat_id, ui_msg_id)
        except:
            pass
        data["ui_msg_id"] = None

    # Try to send via assistant bot (inline)
    try:
        bot_me = await Tele.bot.get_me()
        bot_username = bot_me.username
        if not bot_username:
            raise ValueError("Bot username not found")

        results = await client.get_inline_bot_results(bot_username, f"mus_ui_{chat_id}")
        if results and results.results:
            await client.send_inline_bot_result(
                chat_id,
                results.query_id,
                results.results[0].id
            )
            # Fetch the message ID of the sent inline result
            # We look for a message sent by the userbot but marked as 'via_bot'
            async for msg in client.get_chat_history(chat_id, limit=5):
                if msg.via_bot and msg.via_bot.username == bot_username:
                    data["ui_msg_id"] = msg.id
                    break
            return
    except Exception as e:
        logger.debug(f"Inline fallback triggered for chat {chat_id}: {e}")

    # Fallback to plain text if bot/inline fails
    msg = await client.send_message(chat_id, text)
    data["ui_msg_id"] = msg.id

# --- Logic Core Functions ---
async def play_next(chat_id: int, tgcalls: PyTgCalls):
    """Plays the next song in the queue or cleans up if empty."""
    if chat_id not in streaming_chats:
        return
    
    data = streaming_chats[chat_id]
    current = data["current"]
    loop = data["loop"]
    queue = data["queue"]
    data["is_paused"] = False

    # Cleanup or re-queue current song
    if current:
        if loop == 0:  # No loop
            if os.path.exists(current["path"]):
                try: os.remove(current["path"])
                except: pass
        elif loop == 2:  # Loop queue
            queue.append(current)

    # Determine next track
    if loop == 1 and current:
        next_song = current
    elif queue:
        next_song = queue.pop(0)
    else:
        # End of playback
        if current and loop != 2:
            if os.path.exists(current["path"]):
                try: os.remove(current["path"])
                except: pass
        
        # Delete UI message
        ui_msg_id = data.get("ui_msg_id")
        if ui_msg_id:
            try: await data["client"].delete_messages(chat_id, ui_msg_id)
            except: pass

        data["current"] = None
        try:
            await tgcalls.leave_call(chat_id)
        except:
            pass
            
        if chat_id in streaming_chats:
            del streaming_chats[chat_id]
        return

    data["current"] = next_song
    try:
        await tgcalls.play(chat_id, next_song["path"])
        await send_track_ui(chat_id, next_song)
    except Exception as e:
        logger.error(f"Error playing next song: {e}")
        data["current"] = None
        await play_next(chat_id, tgcalls)

async def skip_track(chat_id: int):
    """Internal function to skip a track."""
    if chat_id not in streaming_chats:
        return False
    
    data = streaming_chats[chat_id]
    tgcalls = Tele.getClientPyTgCalls(data["client"])
    if not tgcalls or not data["current"]:
        return False
        
    old_loop = data["loop"]
    if old_loop == 1:
        data["loop"] = 0
        
    await play_next(chat_id, tgcalls)
    
    if old_loop == 1:
        data["loop"] = 1
    return True

async def stop_music(chat_id: int):
    """Internal function to stop music and clean up."""
    if chat_id not in streaming_chats:
        return False
        
    data = streaming_chats[chat_id]
    tgcalls = Tele.getClientPyTgCalls(data["client"])
    if not tgcalls:
        return False

    if data["current"] and os.path.exists(data["current"]["path"]):
        try: os.remove(data["current"]["path"])
        except: pass
    for song in data["queue"]:
        if os.path.exists(song["path"]):
            try: os.remove(song["path"])
            except: pass
    
    # Delete UI message before clearing session
    ui_msg_id = data.get("ui_msg_id")
    if ui_msg_id:
        try: await data["client"].delete_messages(chat_id, ui_msg_id)
        except: pass

    if chat_id in streaming_chats:
        del streaming_chats[chat_id]
    
    try:
        await tgcalls.leave_call(chat_id)
    except:
        pass
    return True

async def pause_music(chat_id: int) -> bool:
    """Internal function to pause music using pytgcalls 2.x methods."""
    if chat_id not in streaming_chats:
        return False
    data = streaming_chats[chat_id]
    tgcalls = Tele.getClientPyTgCalls(data["client"])
    if not tgcalls or data.get("is_paused"):
        return False
    try:
        # In pytgcalls v2.2.8, the method is pause()
        await tgcalls.pause(chat_id)
        data["is_paused"] = True
        return True
    except Exception as e:
        logger.error(f"Pause failed: {e}")
        return False

async def resume_music(chat_id: int) -> bool:
    """Internal function to resume music using pytgcalls 2.x methods."""
    if chat_id not in streaming_chats:
        return False
    data = streaming_chats[chat_id]
    tgcalls = Tele.getClientPyTgCalls(data["client"])
    if not tgcalls or not data.get("is_paused"):
        return False
    try:
        # In pytgcalls v2.2.8, the method is resume()
        await tgcalls.resume(chat_id)
        data["is_paused"] = False
        return True
    except Exception as e:
        logger.error(f"Resume failed: {e}")
        return False

# --- Userbot Handlers ---
@Tele.on_update(call_filters.stream_end())
async def stream_end_handler(c: PyTgCalls, update: Update):
    await play_next(update.chat_id, c)

@Tele.on_message(filters.command('play') & filters.me)
async def play_command(c: Client, m: Message):
    if len(m.command) < 2: # type: ignore
        return await m.reply("Please provide a song name or link.")
    
    chat_id = m.chat.id # type: ignore
    query = " ".join(m.command[1:]) # type: ignore
    loading = await m.reply('`🔍 Searching and downloading...`')
    
    tgcalls = Tele.getClientPyTgCalls(c)
    if not tgcalls:
        return await loading.edit("Voice chat client not initialized.")
    
    try:
        song_info = await Tele.download_song(query, c)
        if not song_info:
            return await loading.edit("❌ Song not found.")
        song_data: SongDict = song_info  # type: ignore
    except Exception as e:
        return await loading.edit(f"❌ Error: {str(e)}")
    
    if chat_id not in streaming_chats:
        streaming_chats[chat_id] = { # type: ignore
            "queue": [],
            "loop": 0,
            "current": None,
            "client": c,
            "is_paused": False,
            "ui_msg_id": None
        }
    
    data = streaming_chats[chat_id] # type: ignore
    data["client"] = c

    if not data["current"]:
        data["current"] = song_data
        try:
            await tgcalls.play(chat_id, song_data["path"]) # type: ignore
            await loading.delete()
            await send_track_ui(chat_id, song_data) # type: ignore
        except Exception as e:
            await loading.edit(f"❌ Error playing: {e}")
            if os.path.exists(song_data["path"]): os.remove(song_data["path"])
            data["current"] = None
    else:
        data["queue"].append(song_data)
        await loading.edit(get_track_text(song_data, f"📝 Queued (Position: {len(data['queue'])})", data["loop"]))

@Tele.on_message(filters.command(['skip', 'next']) & filters.me)
async def skip_cmd_handler(c: Client, m: Message):
    if await skip_track(m.chat.id): # type: ignore
        await m.reply("⏭ Skipped to next track.")
    else:
        await m.reply("❌ Nothing is playing to skip.")

@Tele.on_message(filters.command('mstop') & filters.me)
async def stop_cmd_handler(c: Client, m: Message):
    if await stop_music(m.chat.id): # type: ignore
        await m.reply("🛑 Stopped playback and cleared queue.")
    else:
        await m.reply("❌ Not in voice chat.")

@Tele.on_message(filters.command('pause') & filters.me)
async def pause_cmd_handler(c: Client, m: Message):
    if await pause_music(m.chat.id): # type: ignore
        await m.reply("⏸ Paused playback.")
    else:
        await m.reply("❌ Already paused or not playing.")

@Tele.on_message(filters.command('resume') & filters.me)
async def resume_cmd_handler(c: Client, m: Message):
    if await resume_music(m.chat.id): # type: ignore
        await m.reply("▶️ Resumed playback.")
    else:
        await m.reply("❌ Already playing or not playing.")

@Tele.on_message(filters.command('queue') & filters.me)
async def queue_cmd_handler(c: Client, m: Message):
    chat_id = m.chat.id # type: ignore
    if chat_id not in streaming_chats:
        return await m.reply("❌ Queue is empty.")
    
    data = streaming_chats[chat_id]
    res = "**🎶 Current Queue:**\n\n"
    if data["current"]:
        curr = data["current"]
        res += f"▶️ **Now Playing:** `{curr['title']}` - `{curr['performer']}`\n"
    
    if data["queue"]:
        res += "\n**🔜 Upcoming:**\n"
        for i, song in enumerate(data["queue"][:10], 1):
            res += f"{i}. `{song['title']}` - `{song['performer']}`\n"
        if len(data["queue"]) > 10:
            res += f"... and {len(data['queue']) - 10} more."
    else:
        if not data["current"]:
            return await m.reply("❌ Queue is empty.")
                
    await m.reply(res)

@Tele.on_message(filters.command('loop') & filters.me)
async def loop_cmd_handler(c: Client, m: Message):
    if not m.chat or not m.command:
        return
        
    chat_id = m.chat.id
    if chat_id not in streaming_chats:
        return await m.reply("❌ No active music session in this chat.")
    
    data = streaming_chats[chat_id]
    cmd_len = len(m.command)
    
    if cmd_len > 1:
        arg = m.command[1].lower()
        if arg in ['off', '0', 'none']:
            data["loop"] = 0
        elif arg in ['track', '1', 'single']:
            data["loop"] = 1
        elif arg in ['queue', '2', 'all']:
            data["loop"] = 2
        else:
            return await m.reply("❌ Invalid loop mode. Use: `off`, `track`, or `queue`.")
    else:
        # Toggle cycle
        data["loop"] = (data["loop"] + 1) % 3
    
    modes = {0: "Off", 1: "Track", 2: "Queue"}
    status_msg = await m.reply(f"🔄 Loop mode set to: **{modes[data['loop']]}**")
    
    # Update UI if current song exists (edit existing instead of new)
    if data["current"]:
        await send_track_ui(chat_id, data["current"], force_new=False)
    
    # Optional: Delete command and status message after 3 seconds
    await asyncio.sleep(3)
    try:
        await m.delete()
        await status_msg.delete()
    except:
        pass

# --- Bot Inline & Callback Handlers ---
@Tele.bot.on_inline_query(filters.regex(r"^mus_ui_(-?\d+)$"))
async def music_inline_handler(c: Client, q: InlineQuery):
    chat_id = int(q.matches[0].group(1))
    if chat_id not in streaming_chats:
        return await q.answer([
            InlineQueryResultArticle(
                title="No Audio",
                input_message_content=InputTextMessageContent("No music active in this chat.")
            )
        ], cache_time=1)
    
    data = streaming_chats[chat_id]
    song = data["current"]
    if not song:
        return await q.answer([])

    await q.answer([
        InlineQueryResultArticle(
            title="Music Player",
            input_message_content=InputTextMessageContent(get_track_text(song, "Now Playing", data["loop"])),
            reply_markup=get_music_keyboard(chat_id, data["loop"], data.get("is_paused", False))
        )
    ], cache_time=1)

@Tele.bot.on_callback_query(filters.regex(r"^mus_(skip|loop|queue|stop|close|pause|resume)_(-?\d+)$"))
async def music_callback_handler(c: Client, q: CallbackQuery):
    action = q.matches[0].group(1)
    chat_id = int(q.matches[0].group(2))

    if not q.from_user:
        return await q.answer("❌ Error: User info not found.")

    if chat_id not in streaming_chats and action != "close":
        return await q.answer("❌ No active music session in this chat.", show_alert=True)

    data = streaming_chats.get(chat_id)
    
    # Permission Check
    if data and not await is_authorized(data["client"], chat_id, q.from_user.id):
        return await q.answer("❌ No permission! Only admins or the owner can do this.", show_alert=True)

    if action == "skip" and data:
        if not data["current"]:
            return await q.answer("❌ Nothing is playing!", show_alert=True)
            
        if not data["queue"] and data["loop"] != 2:
            await q.answer("👋 This was the last song. Leaving...", show_alert=True)
            await stop_music(chat_id)
            if q.message:
                try: await q.edit_message_text("🛑 Music playback stopped.")
                except: pass
            return

        if await skip_track(chat_id):
            await q.answer("⏭ Skipped track!")
        else:
            await q.answer("❌ Failed to skip.", show_alert=True)

    elif action == "loop" and data:
        data["loop"] = (data["loop"] + 1) % 3
        modes = {0: "Off", 1: "Track", 2: "Queue"}
        await q.answer(f"🔄 Loop Mode: {modes[data['loop']]}")
        if data["current"]:
            try:
                await q.edit_message_text(
                    get_track_text(data["current"], "Now Playing", data["loop"]),
                    reply_markup=get_music_keyboard(chat_id, data["loop"], data.get("is_paused", False))
                )
            except: pass

    elif action == "queue" and data:
        res = "📜 Queue:\n"
        if data["current"]:
            res += f"▶️ {data['current']['title']}\n"
        for i, s in enumerate(data["queue"][:5], 1):
            res += f"{i}. {s['title']}\n"
        await q.answer(res, show_alert=True)

    elif action == "stop" and data:
        await stop_music(chat_id)
        await q.answer("🛑 Stopped.")
        if q.message:
            try: await q.edit_message_text("🛑 Music playback stopped.")
            except: pass

    elif action == "pause" and data:
        if not data["current"]:
            return await q.answer("❌ Nothing is playing to pause!", show_alert=True)
        
        if await pause_music(chat_id):
            try:
                await q.edit_message_text(
                    get_track_text(data["current"], "⏸ Paused", data["loop"]), # type: ignore
                    reply_markup=get_music_keyboard(chat_id, data["loop"], True)
                )
                await q.answer("⏸ Paused.")
            except Exception as e:
                logger.debug(f"Edit failed on pause: {e}")
                await q.answer("⏸ Paused.")
        else:
            await q.answer("❌ Already paused or failed to pause.", show_alert=True)

    elif action == "resume" and data:
        if not data["current"]:
            return await q.answer("❌ Nothing is playing to resume!", show_alert=True)
            
        if await resume_music(chat_id):
            try:
                await q.edit_message_text(
                    get_track_text(data["current"], "Now Playing", data["loop"]), # type: ignore
                    reply_markup=get_music_keyboard(chat_id, data["loop"], False)
                )
                await q.answer("▶️ Resumed.")
            except Exception as e:
                logger.debug(f"Edit failed on resume: {e}")
                await q.answer("▶️ Resumed.")
        else:
            await q.answer("❌ Already playing or failed to resume.", show_alert=True)

    elif action == "close":
        ui_msg_id = data.get("ui_msg_id") if data else None
        if data and ui_msg_id:
            try:
                await data["client"].delete_messages(chat_id, ui_msg_id)
                await q.answer("Closed player.")
            except:
                await q.answer("❌ Could not delete player message.")
        else:
            try:
                await q.message.delete()
                await q.answer("Closed player.")
            except:
                # If bot can't delete, just clear the text/markup
                try:
                    await q.edit_message_text("Player closed.")
                except:
                    await q.answer("❌ Could not close player.")

# --- Module Metadata ---
MOD_NAME = "Music"
MOD_HELP = """> `.play <query>`
Download and play a song. Supports searching by title or artist.

> `.skip` / `.next`
Skip the current track.

> `.pause` / `.resume`
Pause or Resume playback.

> `.mstop`
Stop playback and clear the queue.

> `.loop [off|track|queue]`
Set or cycle music loop mode.

> `.queue`
Show the list of upcoming songs.

**Features:**
- **Inline Controls**: Easy buttons to manage playback via assistant bot.
- **Loop Modes**: Off, Track (🔂), or Queue (🔁).
- **Auto-Cleanup**: Temporary files are deleted after use.
- **Metadata**: Full title, artist, and duration display.
"""
