from Hazel import Tele
from pyrogram import Client, filters
from pytgcalls import filters as call_filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from typing import Dict, List, Tuple
import logging
import asyncio
import os

logger = logging.getLogger("Mods.voicechat")

# Structure: {chat_id: {"queue": [(path, title)], "loop": 0, "current": (path, title)}}
# loop modes: 0 - off, 1 - track, 2 - queue
streamingChatsData: Dict[int, dict] = {}

async def play_next(chat_id: int, tgcalls: PyTgCalls):
    if chat_id not in streamingChatsData:
        return
    
    data = streamingChatsData[chat_id]
    current = data.get("current")
    loop = data.get("loop", 0)
    queue = data.get("queue", [])

    # Handle old file cleanup
    if current:
        old_path = current[0]
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
            if os.path.exists(current[0]):
                try: os.remove(current[0])
                except: pass
        data["current"] = None
        try:
            await tgcalls.leave_call(chat_id)
        except:
            pass
        return

    data["current"] = next_song
    try:
        await tgcalls.play(chat_id, next_song[0])
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
    loading = await m.reply('...')
    
    tgcalls = Tele.getClientPyTgCalls(c)
    if not tgcalls:
        return await loading.edit("Voice chat client not initialized.")
    
    try:
        path = await Tele.download_song(query, c)
        if not path:
            return await loading.edit("Song not found.")
    except Exception as e:
        return await loading.edit(f"Error downloading song: {str(e)}")
    
    if chat_id not in streamingChatsData:
        streamingChatsData[chat_id] = {"queue": [], "loop": 0, "current": None}
    
    data = streamingChatsData[chat_id]
    
    if not data["current"]:
        data["current"] = (path, query)
        try:
            await tgcalls.play(chat_id, path)
            await loading.edit(f"Playing: **{query}**")
        except Exception as e:
            await loading.edit(f"Error playing: {e}")
            if os.path.exists(path): os.remove(path)
            data["current"] = None
    else:
        data["queue"].append((path, query))
        await loading.edit(f"Queued **{query}** at position {len(data['queue'])}")

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
    
    await m.reply("Skipped to next.")

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
        res += f"1. {data['current'][1]} (Current)\n"
    else:
        res += "None\n"
    
    if data["queue"]:
        res += "\n**Upcoming:**\n"
        for i, song in enumerate(data["queue"], 2):
            res += f"{i}. {song[1]}\n"
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
        if data["current"] and os.path.exists(data["current"][0]):
            try: os.remove(data["current"][0])
            except: pass
        for path, _ in data["queue"]:
            if os.path.exists(path):
                try: os.remove(path)
                except: pass
        del streamingChatsData[chat_id]
    
    try:
        await tgcalls.leave_call(chat_id)
        await m.reply("Stopped and cleared queue.")
    except:
        await m.reply("Not in call.")

MOD_NAME = "Music"
MOD_HELP = "**Usage:**\n> .play (query)\n> .skip\n> .loop\n> .queue\n> .stop"