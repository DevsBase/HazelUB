from Hazel import Tele
from pyrogram import Client, filters
from pytgcalls import filters as call_filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from typing import Dict, List, Tuple, Optional
import logging
import asyncio
import os

logger = logging.getLogger("Mods.voicechat")

# Structure: {chat_id: {"queue": [song_dict], "loop": 0, "current": song_dict}}
# song_dict: {"path": str, "title": str, "performer": str, "duration": int}
# loop modes: 0 - off, 1 - track, 2 - queue
streamingChatsData: Dict[int, dict] = {}

def get_duration_str(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"

def get_track_info_text(song: dict, status: str = "Playing") -> str:
    title = song.get("title", "Unknown")
    artist = song.get("performer", "Unknown")
    duration = get_duration_str(song.get("duration", 0))
    return (
        f"**{status}**\n"
        f"**🎵 Title:** `{title}`\n"
        f"**👤 Artist:** `{artist}`\n"
        f"**🕒 Duration:** `{duration}`"
    )

async def play_next(chat_id: int, tgcalls: PyTgCalls):
    if chat_id not in streamingChatsData:
        return
    
    data = streamingChatsData[chat_id]
    current = data.get("current")
    loop = data.get("loop", 0)
    queue = data.get("queue", [])
    client = data.get("client")

    # Handle old file cleanup
    if current:
        old_path = current["path"]
        if loop == 0: # No loop: delete old file
            if os.path.exists(old_path):
                try: os.remove(old_path)
                except: pass
        elif loop == 2: # Loop queue: push current to end of queue
            queue.append(current)

    if loop == 1 and current:
        next_song = current
    elif queue:
        next_song = queue.pop(0)
    else:
        # No more songs to play
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
        # Announce next song using the correct client
        if client:
            await client.send_message(chat_id, get_track_info_text(next_song))
    except Exception as e:
        logger.error(f"Error playing next song: {e}")
        data["current"] = None
        await play_next(chat_id, tgcalls)

@Tele.on_update(call_filters.stream_end())
async def streamEndHandler(c: PyTgCalls, update: Update):
    await play_next(update.chat_id, c)

@Tele.on_message(filters.command('play') & filters.me)
async def playFunc(c: Client, m: Message):
    if len(m.command) < 2:
        return await m.reply("Please give a query.")
    
    chat_id = m.chat.id
    query = " ".join(m.command[1:])
    loading = await m.reply('`Searching...`')
    
    tgcalls = Tele.getClientPyTgCalls(c)
    if not tgcalls:
        return await loading.edit("Voice chat client not initialized.")
    
    try:
        song_data = await Tele.download_song(query, c)
        if not song_data:
            return await loading.edit("Song not found.")
    except Exception as e:
        return await loading.edit(f"Error: {str(e)}")
    
    if chat_id not in streamingChatsData:
        streamingChatsData[chat_id] = {"queue": [], "loop": 0, "current": None, "client": c}
    
    data = streamingChatsData[chat_id]
    data["client"] = c # Ensure we use the latest client that sent a play command
    
    if not data["current"]:
        data["current"] = song_data
        try:
            await tgcalls.play(chat_id, song_data["path"])
            await loading.edit(get_track_info_text(song_data))
        except Exception as e:
            await loading.edit(f"Error playing: {e}")
            if os.path.exists(song_data["path"]): os.remove(song_data["path"])
            data["current"] = None
    else:
        data["queue"].append(song_data)
        await loading.edit(get_track_info_text(song_data, f"Queued (Pos: {len(data['queue'])})"))

@Tele.on_message(filters.command('skip') & filters.me)
async def skipFunc(c: Client, m: Message):
    chat_id = m.chat.id
    tgcalls = Tele.getClientPyTgCalls(c)
    if not tgcalls or chat_id not in streamingChatsData or not streamingChatsData[chat_id]["current"]:
        return await m.reply("Nothing is playing.")
    
    data = streamingChatsData[chat_id]
    old_loop = data["loop"]
    if old_loop == 1:
        data["loop"] = 0
    
    await play_next(chat_id, tgcalls)
    
    if old_loop == 1:
        data["loop"] = 1
    
    await m.reply("Skipped to next track.")

@Tele.on_message(filters.command('loop') & filters.me)
async def loopFunc(c: Client, m: Message):
    chat_id = m.chat.id
    if chat_id not in streamingChatsData:
        return await m.reply("Nothing is currently playing.")
    
    data = streamingChatsData[chat_id]
    data["loop"] = (data.get("loop", 0) + 1) % 3
    
    modes = {0: "Off", 1: "Current Track", 2: "Queue"}
    await m.reply(f"Loop mode set to: **{modes[data['loop']]}**")

@Tele.on_message(filters.command('queue') & filters.me)
async def queueFunc(c: Client, m: Message):
    chat_id = m.chat.id
    if chat_id not in streamingChatsData or (not streamingChatsData[chat_id]["current"] and not streamingChatsData[chat_id]["queue"]):
        return await m.reply("Queue is empty.")
    
    data = streamingChatsData[chat_id]
    res = "**Current Playing:**\n"
    if data["current"]:
        curr = data["current"]
        res += f"1. {curr['title']} - {curr['performer']} ({get_duration_str(curr['duration'])})\n"
    else:
        res += "None\n"
    
    if data["queue"]:
        res += "\n**Upcoming:**\n"
        for i, song in enumerate(data["queue"], 2):
            res += f"{i}. {song['title']} - {song['performer']} ({get_duration_str(song.get('duration', 0))})\n"
            if i > 11:
                res += "..."
                break
                
    await m.reply(res)

@Tele.on_message(filters.command('stop') & filters.me)
async def stopFunc(c: Client, m: Message):
    chat_id = m.chat.id
    tgcalls = Tele.getClientPyTgCalls(c)
    if not tgcalls:
        return
    
    if chat_id in streamingChatsData:
        data = streamingChatsData[chat_id]
        if data["current"] and os.path.exists(data["current"]["path"]):
            try: os.remove(data["current"]["path"])
            except: pass
        for song in data["queue"]:
            if os.path.exists(song["path"]):
                try: os.remove(song["path"])
                except: pass
        del streamingChatsData[chat_id]
    
    try:
        await tgcalls.leave_call(chat_id)
        await m.reply("Stopped and cleared queue.")
    except:
        await m.reply("Not in call.")

MOD_NAME = "Music"
MOD_HELP = """
**Music Commands:**

> `.play <query>`
Download and play a song in voice chat. If music is already playing, it will be added to the queue. Uses actual song metadata (title/artist).

> `.skip`
Skips the current track and plays the next one in the queue.

> `.loop`
Cycles through loop modes:
- **Off**: Play once and move on.
- **Track**: Replay the current song.
- **Queue**: When the queue ends, start over from the first song.

> `.queue`
Display the current track and upcoming songs in the queue.

> `.stop`
Leaves the voice chat and clears the entire queue and all temporary files.

**Features:**
- Automatic playback of the next song.
- Full metadata display (Author, Duration, Title).
- Unique filename system to prevent playback collisions.
- Smart file cleanup.
"""