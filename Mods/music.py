from typing import Dict, List, Optional, TypedDict, Union
import logging
import asyncio
import os

from pyrogram import Client, filters
from pyrogram.types import (
    Message, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    CallbackQuery,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent
)
from pyrogram.errors import BadRequest
from pytgcalls import filters as call_filters
from pytgcalls import PyTgCalls
from pytgcalls.types import Update

from Hazel import Tele

# --- Logging Setup ---
logger = logging.getLogger("HazelUB.Music")

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

# --- Global State ---
streaming_chats: Dict[int, SessionData] = {}

# --- Helper Functions ---
def get_duration_str(seconds: int) -> str:
    """Converts seconds to MM:SS format."""
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"

def get_track_text(song: SongDict, status: str = "Now Playing", loop_mode: int = 0) -> str:
    """Generates the formatted text for a track."""
    modes = {0: "Off", 1: "🔂 Track", 2: "🔁 Queue"}
    return (
        f"**{status}**\n\n"
        f"**🎵 Title:** `{song['title']}`\n"
        f"**👤 Artist:** `{song['performer']}`\n"
        f"**🕒 Duration:** `{get_duration_str(song['duration'])}`\n"
        f"**🔄 Loop:** `{modes.get(loop_mode, 'Off')}`"
    )

def get_music_keyboard(chat_id: int, loop_mode: int) -> InlineKeyboardMarkup:
    """Creates the control keyboard for the music player."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏭ Skip", callback_data=f"mus_skip_{chat_id}"),
            InlineKeyboardButton("🔄 Loop", callback_data=f"mus_loop_{chat_id}"),
        ],
        [
            InlineKeyboardButton("📜 Queue", callback_data=f"mus_queue_{chat_id}"),
            InlineKeyboardButton("🛑 Stop", callback_data=f"mus_stop_{chat_id}"),
        ]
    ])

async def send_track_ui(chat_id: int, song: SongDict, status: str = "Now Playing"):
    """Sends the track UI, attempting inline buttons first, then falling back to text."""
    data = streaming_chats.get(chat_id)
    if not data:
        return
    
    loop_mode = data["loop"]
    text = get_track_text(song, status, loop_mode)
    client = data["client"]

    # Try to send via assistant bot (inline)
    try:
        bot_me = await Tele.bot.get_me()
        # Querying the bot for an inline result that contains our buttons
        # We pass the chat_id in the query so the inline handler knows what to show
        results = await client.get_inline_bot_results(bot_me.username, f"mus_ui_{chat_id}")
        if results.results:
            await client.send_inline_bot_result(
                chat_id,
                results.query_id,
                results.results[0].id
            )
            return
    except Exception as e:
        logger.debug(f"Inline fallback triggered for chat {chat_id}: {e}")

    # Fallback to plain text if bot/inline fails
    await client.send_message(chat_id, text)

# --- Core Logic ---
async def play_next(chat_id: int, tgcalls: PyTgCalls):
    """Plays the next song in the queue or cleans up if empty."""
    if chat_id not in streaming_chats:
        return
    
    data = streaming_chats[chat_id]
    current = data["current"]
    loop = data["loop"]
    queue = data["queue"]

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
        data["current"] = None
        try:
            await tgcalls.leave_call(chat_id)
        except:
            pass
        return

    data["current"] = next_song
    try:
        await tgcalls.play(chat_id, next_song["path"])
        await send_track_ui(chat_id, next_song)
    except Exception as e:
        logger.error(f"Error playing next song: {e}")
        data["current"] = None
        await play_next(chat_id, tgcalls)

# --- Userbot Handlers ---
@Tele.on_update(call_filters.stream_end())
async def stream_end_handler(c: PyTgCalls, update: Update):
    await play_next(update.chat_id, c)

@Tele.on_message(filters.command('play') & filters.me)
async def play_command(c: Client, m: Message):
    if len(m.command) < 2:
        return await m.reply("Please provide a song name or link.")
    
    chat_id = m.chat.id
    query = " ".join(m.command[1:])
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
        streaming_chats[chat_id] = {
            "queue": [],
            "loop": 0,
            "current": None,
            "client": c
        }
    
    data = streaming_chats[chat_id]
    data["client"] = c

    if not data["current"]:
        data["current"] = song_data
        try:
            await tgcalls.play(chat_id, song_data["path"])
            await loading.delete()
            await send_track_ui(chat_id, song_data)
        except Exception as e:
            await loading.edit(f"❌ Error playing: {e}")
            if os.path.exists(song_data["path"]): os.remove(song_data["path"])
            data["current"] = None
    else:
        data["queue"].append(song_data)
        await loading.edit(get_track_text(song_data, f"📝 Queued (Position: {len(data['queue'])})", data["loop"]))

@Tele.on_message(filters.command(['skip', 'next']) & filters.me)
async def skip_command(c: Client, m: Message):
    chat_id = m.chat.id
    tgcalls = Tele.getClientPyTgCalls(c)
    if not tgcalls or chat_id not in streaming_chats or not streaming_chats[chat_id]["current"]:
        return await m.reply("❌ Nothing is playing to skip.")
    
    data = streaming_chats[chat_id]
    # If looping current track, bypass it for skip
    original_loop = data["loop"]
    if original_loop == 1:
        data["loop"] = 0
    
    await play_next(chat_id, tgcalls)
    
    if original_loop == 1:
        data["loop"] = 1
    
    if m.from_user: # Only reply if it was a command (and not an internal call)
        await m.reply("⏭ Skipped to next track.")

@Tele.on_message(filters.command('mstop') & filters.me)
async def stop_command(c: Client, m: Message):
    chat_id = m.chat.id
    tgcalls = Tele.getClientPyTgCalls(c)
    if not tgcalls:
        return
    
    if chat_id in streaming_chats:
        data = streaming_chats[chat_id]
        if data["current"] and os.path.exists(data["current"]["path"]):
            try: os.remove(data["current"]["path"])
            except: pass
        for song in data["queue"]:
            if os.path.exists(song["path"]):
                try: os.remove(song["path"])
                except: pass
        del streaming_chats[chat_id]
    
    try:
        await tgcalls.leave_call(chat_id)
        await m.reply("🛑 Stopped playback and cleared queue.")
    except:
        await m.reply("❌ Not in voice chat.")

@Tele.on_message(filters.command('queue') & filters.me)
async def queue_command(c: Client, m: Message):
    chat_id = m.chat.id
    if chat_id not in streaming_chats:
        return await m.reply("❌ Queue is empty.")
    
    data = streaming_chats[chat_id]
    res = "**🎶 Current Queue:**\n\n"
    if data["current"]:
        curr = data["current"]
        res += f"▶️ **Now:** `{curr['title']}` - `{curr['performer']}`\n"
    
    if data["queue"]:
        res += "\n**🔜 Next Up:**\n"
        for i, song in enumerate(data["queue"][:10], 1):
            res += f"{i}. `{song['title']}` - `{song['performer']}`\n"
        if len(data["queue"]) > 10:
            res += f"... and {len(data['queue']) - 10} more."
    else:
        if not data["current"]:
            return await m.reply("❌ Queue is empty.")
                
    await m.reply(res)

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
            reply_markup=get_music_keyboard(chat_id, data["loop"])
        )
    ], cache_time=1)

@Tele.bot.on_callback_query(filters.regex(r"^mus_(skip|loop|queue|stop)_(-?\d+)$"))
async def music_callback_handler(c: Client, q: CallbackQuery):
    action = q.matches[0].group(1)
    chat_id = int(q.matches[0].group(2))

    # Check permission (only userbot owner)
    if not q.from_user or not Tele.mainClient.me or q.from_user.id != Tele.mainClient.me.id:
        return await q.answer("❌ You are not authorized to control this player.", show_alert=True)

    if chat_id not in streaming_chats:
        return await q.answer("❌ No active session found.", show_alert=True)

    data = streaming_chats[chat_id]
    tgcalls = Tele.getClientPyTgCalls(data["client"])

    if action == "skip":
        if not data["current"]:
            return await q.answer("❌ Nothing is playing to skip.", show_alert=True)
            
        if not q.message or not q.message.chat:
            return await q.answer("❌ Message context lost.", show_alert=True)
            
        # Reuse userbot skip logic
        await skip_command(data["client"], Message(id=0, chat=q.message.chat)) 
        await q.answer("⏭ Skipped.")

    elif action == "loop":
        data["loop"] = (data["loop"] + 1) % 3
        modes = {0: "Off", 1: "Track", 2: "Queue"}
        await q.answer(f"🔄 Loop Mode: {modes[data['loop']]}")
        # Update original UI message
        if data["current"]:
            await q.edit_message_text(
                get_track_text(data["current"], "Now Playing", data["loop"]),
                reply_markup=get_music_keyboard(chat_id, data["loop"])
            )

    elif action == "queue":
        res = "📜 **Queue:**\n"
        if data["current"]:
            res += f"▶️ {data['current']['title']}\n"
        for i, s in enumerate(data["queue"][:5], 1):
            res += f"{i}. {s['title']}\n"
        await q.answer(res, show_alert=True)

    elif action == "stop":
        if not q.message or not q.message.chat:
            return await q.answer("❌ Message context lost.", show_alert=True)
            
        await stop_command(data["client"], Message(id=0, chat=q.message.chat))
        await q.answer("🛑 Stopped.")
        await q.edit_message_text("🛑 Music playback stopped.")

# --- Module Metadata ---
MOD_NAME = "Music"
MOD_HELP = """> `.play <query>`
Download and play a song. Supports searching by title or artist.

> `.skip` / `.next`
Skip the current track.

> `.mstop`
Stop playback and clear the queue.

> `.queue`
Show the list of upcoming songs.

**Features:**
- ✨ **Inline Controls**: Easy buttons to manage playback via assistant bot.
- 🔁 **Loop Modes**: Off, Track (🔂), or Queue (🔁).
- 🔊 **Auto-Cleanup**: Temporary files are deleted after use.
- 🎵 **Metadata**: Full title, artist, and duration display.
"""
