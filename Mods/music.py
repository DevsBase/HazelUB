import asyncio
import logging
import os
from typing import Dict, List, Optional, TypedDict, Union

import aiohttp
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.enums import ButtonStyle
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)
from pytgcalls import PyTgCalls
from pytgcalls import filters as call_filters
from pytgcalls.types import Update

from config import LRCLIB
from Hazel import Tele, sudoers

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
# Structure: { client_user_id: { chat_id: SessionData } }
streaming_chats: Dict[int, Dict[int, SessionData]] = {}


def _get_session(client_id: int, chat_id: int) -> Optional[SessionData]:
    """Returns the SessionData for a given client + chat, or None."""
    return streaming_chats.get(client_id, {}).get(chat_id)


# --- Helper Functions ---
def get_audio_duration(file_path: str) -> int:
    """Helper to get audio duration using ffprobe."""
    try:
        import subprocess

        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            file_path,
        ]
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        return int(float(result.stdout.strip()))
    except:
        return 0


async def fetch_lyrics(title: str, artist: str, duration: int) -> str:
    url = f"{LRCLIB}/api/search"
    if artist and artist.lower() != "unknown artist":
        params = {"track_name": title, "artist_name": artist}
    else:
        params = {"q": title}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    results = await resp.json()
                    if isinstance(results, list) and results:
                        best_match = None
                        for res in results:
                            res_dur = res.get("duration", 0)
                            if abs(res_dur - duration) <= 2:
                                best_match = res
                                break
                        if not best_match:
                            best_match = results[0]
                        return best_match.get("plainLyrics", "")
    except Exception as e:
        logger.error(f"Error fetching lyrics: {e}")
    return ""


def get_duration_str(seconds: Union[int, float]) -> str:
    """Converts seconds to MM:SS format."""
    minutes, sec = divmod(int(seconds), 60)
    return f"{minutes:02d}:{sec:02d}"


def get_track_text(
    song: SongDict, status: str = "Now Playing", loop_mode: int = 0
) -> str:
    """Generates the formatted text for a track."""
    modes = {0: "Off", 1: "Track", 2: "Queue"}
    return (
        f"**{status}**\n\n"
        f"**Title:** `{song['title']}`\n"
        f"**Artist:** `{song['performer']}`\n"
        f"**Duration:** `{get_duration_str(song['duration'])}`\n"
        f"**Loop Mode:** `{modes.get(loop_mode, 'Off')}`"
    )


def get_music_keyboard(
    chat_id: int, loop_mode: int, is_paused: bool = False
) -> InlineKeyboardMarkup:
    """Creates the control keyboard for the music player."""
    pause_resume_text = "▶️ Resume" if is_paused else "⏸ Pause"
    pause_resume_cb = f"mus_resume_{chat_id}" if is_paused else f"mus_pause_{chat_id}"

    return InlineKeyboardMarkup(
        [
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
                InlineKeyboardButton(
                    "📝 Lyrics", callback_data=f"mus_lyrics_{chat_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    "Close Player",
                    callback_data=f"mus_close_{chat_id}",
                    style=ButtonStyle.DANGER,
                )
            ],
        ]
    )


async def is_authorized(client: Client, chat_id: int, user_id: int) -> bool:
    """Checks if a user is authorized to control the music (sudo or admin)."""
    if sudoers.get(getattr(client.me, "id")) and user_id in sudoers[user_id]:
        return True
    for ub_client in Tele._allClients:
        if ub_client.me and ub_client.me.id == user_id:
            return True
    try:
        return await Tele.is_admin(client, chat_id, user_id)
    except Exception as e:
        logger.error(f"Admin check failed: {e}")
        return False


async def send_track_ui(
    client_id: int,
    chat_id: int,
    song: SongDict,
    status: str = "Now Playing",
    force_new: bool = True,
) -> None:
    """Sends the track UI, attempting to edit existing if force_new is False."""
    data = _get_session(client_id, chat_id)
    if not data:
        return

    loop_mode = data["loop"]
    is_paused = data.get("is_paused", False)
    text = get_track_text(song, status, loop_mode)
    client = data["client"]

    ui_msg_id = data.get("ui_msg_id")
    if not force_new and ui_msg_id:
        try:
            await client.edit_message_text(
                chat_id,
                ui_msg_id,
                text,
                reply_markup=get_music_keyboard(chat_id, loop_mode, is_paused),
            )
            return
        except Exception as e:
            logger.debug(f"Edit failed (falling back to new message): {e}")

    if ui_msg_id:
        try:
            await client.delete_messages(chat_id, ui_msg_id)
        except:
            pass
        data["ui_msg_id"] = None

    # Try to send via assistant bot (inline)
    try:
        bot_me = Tele.bot.me
        bot_username = bot_me.username  # type: ignore
        if not bot_username:
            raise ValueError("Bot username not found")

        results = await client.get_inline_bot_results(bot_username, f"mus_ui_{chat_id}")
        if results and results.results:
            await client.send_inline_bot_result(
                chat_id, results.query_id, results.results[0].id
            )
            async for msg in client.get_chat_history(chat_id, limit=5):
                if msg.via_bot and msg.via_bot.username == bot_username:
                    data["ui_msg_id"] = msg.id
                    break
            return
    except Exception as e:
        logger.debug(f"Inline fallback triggered for chat {chat_id}: {e}")

    # Fallback to plain text
    msg = await client.send_message(chat_id, text)
    data["ui_msg_id"] = msg.id


# --- Logic Core Functions ---
async def play_next(client_id: int, chat_id: int, tgcalls: PyTgCalls) -> None:
    """Plays the next song in the queue or cleans up if empty."""
    data = _get_session(client_id, chat_id)
    if not data:
        return

    current = data["current"]
    loop = data["loop"]
    queue = data["queue"]
    data["is_paused"] = False

    if current:
        if loop == 0:
            if await asyncio.to_thread(os.path.exists, current["path"]):
                try:
                    await asyncio.to_thread(os.remove, current["path"])
                except:
                    pass
        elif loop == 2:
            queue.append(current)

    if loop == 1 and current:
        next_song = current
    elif queue:
        next_song = queue.pop(0)
    else:
        if current and loop != 2:
            if await asyncio.to_thread(os.path.exists, current["path"]):
                try:
                    await asyncio.to_thread(os.remove, current["path"])
                except:
                    pass

        ui_msg_id = data.get("ui_msg_id")
        if ui_msg_id:
            try:
                await data["client"].delete_messages(chat_id, ui_msg_id)
            except:
                pass

        data["current"] = None
        try:
            try:
                await tgcalls.play(chat_id)
            except:
                pass
            await tgcalls.leave_call(chat_id)
        except:
            pass

        if client_id in streaming_chats and chat_id in streaming_chats[client_id]:
            del streaming_chats[client_id][chat_id]
            if not streaming_chats[client_id]:
                del streaming_chats[client_id]
        return

    data["current"] = next_song
    try:
        await tgcalls.play(chat_id, next_song["path"])
        await send_track_ui(client_id, chat_id, next_song)
    except Exception as e:
        logger.error(f"Error playing next song: {e}")
        data["current"] = None
        await play_next(client_id, chat_id, tgcalls)


async def skip_track(client_id: int, chat_id: int) -> bool:
    """Internal function to skip a track."""
    data = _get_session(client_id, chat_id)
    if not data:
        return False

    tgcalls = Tele.getClientPyTgCalls(data["client"])
    if not tgcalls or not data["current"]:
        return False

    old_loop = data["loop"]
    if old_loop == 1:
        data["loop"] = 0

    await play_next(client_id, chat_id, tgcalls)

    if old_loop == 1:
        data["loop"] = 1
    return True


async def stop_music(client_id: int, chat_id: int) -> bool:
    """Internal function to stop music and clean up."""
    data = _get_session(client_id, chat_id)
    if not data:
        return False

    tgcalls = Tele.getClientPyTgCalls(data["client"])
    if not tgcalls:
        return False

    if data["current"] and os.path.exists(data["current"]["path"]):
        try:
            os.remove(data["current"]["path"])
        except:
            pass
    for song in data["queue"]:
        if await asyncio.to_thread(os.path.exists, song["path"]):
            try:
                await asyncio.to_thread(os.remove, song["path"])
            except:
                pass

    ui_msg_id = data.get("ui_msg_id")
    if ui_msg_id:
        try:
            await data["client"].delete_messages(chat_id, ui_msg_id)
        except:
            pass

    if client_id in streaming_chats and chat_id in streaming_chats[client_id]:
        del streaming_chats[client_id][chat_id]
        if not streaming_chats[client_id]:
            del streaming_chats[client_id]

    try:
        await tgcalls.leave_call(chat_id)
    except:
        pass
    return True


async def pause_music(client_id: int, chat_id: int) -> bool:
    """Internal function to pause music."""
    data = _get_session(client_id, chat_id)
    if not data:
        return False
    tgcalls = Tele.getClientPyTgCalls(data["client"])
    if not tgcalls or data.get("is_paused"):
        return False
    try:
        await tgcalls.pause(chat_id)
        data["is_paused"] = True
        return True
    except Exception as e:
        logger.error(f"Pause failed: {e}")
        return False


async def resume_music(client_id: int, chat_id: int) -> bool:
    """Internal function to resume music."""
    data = _get_session(client_id, chat_id)
    if not data:
        return False
    tgcalls = Tele.getClientPyTgCalls(data["client"])
    if not tgcalls or not data.get("is_paused"):
        return False
    try:
        await tgcalls.resume(chat_id)
        data["is_paused"] = False
        return True
    except Exception as e:
        logger.error(f"Resume failed: {e}")
        return False


# --- Userbot Handlers ---
@Tele.on_update(call_filters.stream_end())
async def stream_end_handler(c: PyTgCalls, update: Update) -> None:
    # Find which client owns this tgcalls instance
    for ub_client in Tele._allClients:
        tc = Tele.getClientPyTgCalls(ub_client)
        if tc is c and ub_client.me:
            await play_next(ub_client.me.id, update.chat_id, c)
            return


@Tele.on_message(filters.command("play"), sudo=True)
async def play_command(c: Client, m: Message) -> None:
    if not m.chat or not m.command or m.chat.id is None or not c.me:
        return
    chat_id: int = m.chat.id
    client_id: int = c.me.id
    tgcalls = Tele.getClientPyTgCalls(c)
    if not tgcalls:
        return await m.reply("Voice chat client not initialized.")  # type: ignore

    m_command = m.command or []
    query = " ".join(m_command[1:]) if len(m_command) > 1 else ""

    song_data: Optional[SongDict] = None
    loading: Optional[Message] = None

    if m.reply_to_message:
        rm = m.reply_to_message
        media = rm.audio or rm.video or rm.voice
        if media:
            loading = await m.reply("📥 Downloading...")
            try:
                import random
                import string

                random_str = "".join(
                    random.choices(string.ascii_lowercase + string.digits, k=6)
                )
                unique_name = (
                    f"hazel_{int(asyncio.get_event_loop().time())}_{random_str}"
                )

                ext = ".mp4" if rm.video else ".mp3"
                path = str(await c.download_media(rm, file_name=unique_name + ext))  # type: ignore
                final_path = path

                duration = getattr(media, "duration", 0) or 0
                if not duration:
                    duration = get_audio_duration(final_path)

                song_data = SongDict(
                    path=final_path,
                    title=getattr(media, "title", None)
                    or getattr(media, "file_name", None)
                    or ("Voice Message" if rm.voice else "Replied Media"),
                    performer=getattr(media, "performer", None) or "Unknown Artist",
                    duration=duration,
                    file_name=os.path.basename(final_path),
                )
            except Exception as e:
                if loading:
                    await loading.edit(f"Download failed: {e}")
                return
        else:
            await m.reply("Please reply to an audio, video, or voice message.")
            return

    if not song_data:
        if not query:
            await m.reply("Provide a song name or reply to a media file.")
            return

        loading = await m.reply("🔍 Searching...")
        try:
            song_info = await Tele.download_song(query, c)
            if not song_info:
                await loading.edit("Song not found.")
                return
            song_data = song_info  # type: ignore
        except Exception as e:
            msg = f"Error: {str(e)}"
            if loading:
                await loading.edit(msg)
            else:
                await m.reply(msg)
            return

    if not song_data:
        return

    # Create session bucket for this client if not exists
    if client_id not in streaming_chats:
        streaming_chats[client_id] = {}

    if chat_id not in streaming_chats[client_id]:
        try:
            await tgcalls.leave_call(chat_id)
        except:
            ...
        streaming_chats[client_id][chat_id] = SessionData(
            queue=[],
            loop=0,
            current=None,
            client=c,
            is_paused=False,
            ui_msg_id=None,
        )

    data = streaming_chats[client_id][chat_id]
    data["client"] = c

    if not data["current"]:
        data["current"] = song_data
        try:
            await tgcalls.play(chat_id, song_data["path"])
            if loading:
                await loading.delete()
            await send_track_ui(client_id, chat_id, song_data)
        except Exception as e:
            if loading:
                await loading.edit(f"Error playing: {e}")
            else:
                await m.reply(f"Error playing: {e}")
            if os.path.exists(song_data["path"]):
                os.remove(song_data["path"])
            data["current"] = None
    else:
        data["queue"].append(song_data)
        text = get_track_text(
            song_data, f"📝 Queued (Position: {len(data['queue'])})", data["loop"]
        )
        if loading:
            await loading.edit(text)
        else:
            await m.reply(text)


@Tele.on_message(filters.command(["skip", "next"]), sudo=True)
async def skip_cmd_handler(c: Client, m: Message) -> None:
    if not m.chat or m.chat.id is None or not c.me:
        return
    chat_id: int = m.chat.id
    client_id: int = c.me.id
    if await skip_track(client_id, chat_id):
        await m.reply("Skipped.")
    else:
        await m.reply("Nothing is playing to skip.")


@Tele.on_message(filters.command("mstop"), sudo=True)
async def stop_cmd_handler(c: Client, m: Message) -> None:
    if not m.chat or m.chat.id is None or not c.me:
        return
    chat_id: int = m.chat.id
    client_id: int = c.me.id
    if await stop_music(client_id, chat_id):
        await m.reply("Stopped.")
    else:
        await m.reply("Not in voice chat.")


@Tele.on_message(filters.command("pause"), sudo=True)
async def pause_cmd_handler(c: Client, m: Message) -> None:
    if not m.chat or m.chat.id is None or not c.me:
        return
    chat_id: int = m.chat.id
    client_id: int = c.me.id
    if await pause_music(client_id, chat_id):
        await m.reply("Paused playback.")
    else:
        await m.reply("Already paused or not playing.")


@Tele.on_message(filters.command("resume"), sudo=True)
async def resume_cmd_handler(c: Client, m: Message) -> None:
    if not m.chat or m.chat.id is None or not c.me:
        return
    chat_id: int = m.chat.id
    client_id: int = c.me.id
    if await resume_music(client_id, chat_id):
        await m.reply("Resumed playback.")
    else:
        await m.reply("Already playing or not playing.")


@Tele.on_message(filters.command("queue"), sudo=True)
async def queue_cmd_handler(c: Client, m: Message) -> None:
    if not m.chat or m.chat.id is None or not c.me:
        return
    chat_id: int = m.chat.id
    client_id: int = c.me.id

    data = _get_session(client_id, chat_id)
    if not data:
        await m.reply("Queue is empty.")
        return

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
    elif not data["current"]:
        await m.reply("Queue is empty.")
        return

    await m.reply(res)


@Tele.on_message(filters.command("loop"), sudo=True)
async def loop_cmd_handler(c: Client, m: Message) -> None:
    if not m.chat or not m.command or m.chat.id is None or not c.me:
        return
    chat_id: int = m.chat.id
    client_id: int = c.me.id
    data = _get_session(client_id, chat_id)
    if not data:
        await m.reply("No active music session in this chat.")
        return

    cmd_len = len(m.command)
    if cmd_len > 1:
        arg = m.command[1].lower()
        if arg in ["off", "0", "none"]:
            data["loop"] = 0
        elif arg in ["track", "1", "single"]:
            data["loop"] = 1
        elif arg in ["queue", "2", "all"]:
            data["loop"] = 2
        else:
            await m.reply("Invalid loop mode. Use: `off`, `track`, or `queue`.")
            return
    else:
        data["loop"] = (data["loop"] + 1) % 3

    modes = {0: "Off", 1: "Track", 2: "Queue"}
    status_msg = await m.reply(f"🔄 Loop mode set to: **{modes[data['loop']]}**")

    if data["current"]:
        await send_track_ui(client_id, chat_id, data["current"], force_new=False)

    await asyncio.sleep(3)
    try:
        await m.delete()
        await status_msg.delete()
    except:
        pass


# --- Bot Inline & Callback Handlers ---
@Tele.bot.on_inline_query(filters.regex(r"^mus_ui_(-?\d+)$"))
async def music_inline_handler(c: Client, q: InlineQuery) -> None:
    chat_id = int(q.matches[0].group(1))
    song: Optional[SongDict] = None
    loop_mode = 0
    is_paused = False
    for _, sessions in streaming_chats.items():
        if chat_id in sessions:
            d = sessions[chat_id]
            song = d["current"]
            loop_mode = d["loop"]
            is_paused = d.get("is_paused", False)
            break

    if not song:
        await q.answer(
            [
                InlineQueryResultArticle(
                    title="No Audio",
                    input_message_content=InputTextMessageContent(
                        "No music active in this chat."
                    ),
                )
            ],
            cache_time=1,
        )
        return

    await q.answer(
        [
            InlineQueryResultArticle(
                title="Music Player",
                input_message_content=InputTextMessageContent(
                    get_track_text(song, "Now Playing", loop_mode)
                ),
                reply_markup=get_music_keyboard(chat_id, loop_mode, is_paused),
            )
        ],
        cache_time=1,
    )


@Tele.bot.on_callback_query(
    filters.regex(r"^mus_(skip|loop|queue|stop|close|pause|resume|lyrics)_(-?\d+)$")
)
async def music_callback_handler(c: Client, q: CallbackQuery) -> None:
    action = q.matches[0].group(1)
    chat_id = int(q.matches[0].group(2))

    if not q.from_user:
        await q.answer("Error: User info not found.")
        return

    # Find session for this chat (any client)
    data: Optional[SessionData] = None
    owner_client_id: Optional[int] = None
    for cid, sessions in streaming_chats.items():
        if chat_id in sessions:
            data = sessions[chat_id]
            owner_client_id = cid
            break

    if not data and action != "close":
        await q.answer("No active music session in this chat.", show_alert=True)
        return

    if data and not await is_authorized(data["client"], chat_id, q.from_user.id):
        await q.answer(
            "No permission! Only admins or the owner can do this.", show_alert=True
        )
        return

    if action == "skip" and data and owner_client_id:
        if not data["current"]:
            await q.answer("Nothing is playing!", show_alert=True)
            return

        if not data["queue"] and data["loop"] != 2:
            await q.answer("👋 Last song. Leaving...", show_alert=True)
            await stop_music(owner_client_id, chat_id)
            if q.message:
                try:
                    await q.edit_message_text("Stopped.")
                except:
                    pass
            return

        if await skip_track(owner_client_id, chat_id):
            await q.answer("Skipped!")
        else:
            await q.answer("Failed to skip.", show_alert=True)

    elif action == "loop" and data:
        data["loop"] = (data["loop"] + 1) % 3
        modes = {0: "Off", 1: "Track", 2: "Queue"}
        await q.answer(f"🔄 Loop Mode: {modes[data['loop']]}")
        if data["current"]:
            try:
                await q.edit_message_text(
                    get_track_text(data["current"], "Now Playing", data["loop"]),
                    reply_markup=get_music_keyboard(
                        chat_id, data["loop"], data.get("is_paused", False)
                    ),
                )
            except:
                pass

    elif action == "queue" and data:
        res = "📜 Queue:\n"
        if data["current"]:
            res += f"▶️ {data['current']['title']}\n"
        for i, s in enumerate(data["queue"][:5], 1):
            res += f"{i}. {s['title']}\n"
        await q.answer(res, show_alert=True)

    elif action == "stop" and data and owner_client_id:
        await stop_music(owner_client_id, chat_id)
        await q.answer("Stopped.")
        if q.message:
            try:
                await q.edit_message_text("Stopped.")
            except:
                pass

    elif action == "pause" and data and owner_client_id:
        if not data["current"]:
            await q.answer("Nothing is playing to pause!", show_alert=True)
            return

        if await pause_music(owner_client_id, chat_id):
            try:
                await q.edit_message_text(
                    get_track_text(data["current"], "⏸ Paused", data["loop"]),
                    reply_markup=get_music_keyboard(chat_id, data["loop"], True),
                )
                await q.answer("Paused.")
            except Exception as e:
                logger.debug(f"Edit failed on pause: {e}")
                await q.answer("Paused.")
        else:
            await q.answer("Already paused.", show_alert=True)

    elif action == "resume" and data and owner_client_id:
        if not data["current"]:
            await q.answer("Nothing is playing to resume!", show_alert=True)
            return

        if await resume_music(owner_client_id, chat_id):
            try:
                await q.edit_message_text(
                    get_track_text(data["current"], "Now Playing", data["loop"]),
                    reply_markup=get_music_keyboard(chat_id, data["loop"], False),
                )
                await q.answer("Resumed.")
            except Exception as e:
                logger.debug(f"Edit failed on resume: {e}")
                await q.answer("Resumed.")
        else:
            await q.answer("Already playing.", show_alert=True)

    elif action == "lyrics" and data and owner_client_id:
        if not data["current"]:
            await q.answer("Nothing is playing to fetch lyrics for!", show_alert=True)
            return

        await q.answer("Fetching...", show_alert=False)
        lyrics_text = await fetch_lyrics(
            data["current"]["title"],
            data["current"]["performer"],
            data["current"]["duration"],
        )
        if lyrics_text:
            if len(lyrics_text) > 4000:
                lyrics_text = lyrics_text[:4000] + "..."
            try:
                await data["client"].send_message(
                    chat_id,
                    f"**Lyrics for {data['current']['title']}:**\n\n`{lyrics_text}`",
                )
            except Exception as e:
                logger.debug(f"Could not send lyrics: {e}")
        else:
            try:
                await data["client"].send_message(
                    chat_id, "Lyrics not found for this track."
                )
            except:
                pass

    elif action == "close":
        ui_msg_id = data.get("ui_msg_id") if data else None
        if data and ui_msg_id:
            try:
                await data["client"].delete_messages(chat_id, ui_msg_id)
                await q.answer("Closed.")
            except:
                await q.answer("Could not delete player message.")
        else:
            try:
                await q.edit_message_text("Closed.")
            except:
                await q.answer("Could not close player.")


@Tele.on_message(filters.command("lyrics"), sudo=True)
async def lyrics_cmd_handler(c: Client, m: Message) -> None:
    if not m.chat or m.chat.id is None or not c.me:
        return
    chat_id: int = m.chat.id
    client_id: int = c.me.id

    data = _get_session(client_id, chat_id)
    if not data or not data["current"]:
        await m.reply("There is no music currently playing to fetch lyrics for.")
        return

    loading = await m.reply("🔍 Fetching...")
    lyrics_text = await fetch_lyrics(
        data["current"]["title"],
        data["current"]["performer"],
        data["current"]["duration"],
    )

    if lyrics_text:
        if len(lyrics_text) > 4000:
            lyrics_text = lyrics_text[:4000] + "..."
        await loading.edit(
            f"**Lyrics for {data['current']['title']}:**\n\n`{lyrics_text}`"
        )
    else:
        await loading.edit("Lyrics not found.")


# --- Module Metadata ---
MOD_NAME = "Music"
MOD_HELP = """> `.play <query>`
Download and play a song. Supports searching by title or artist.

> `.lyrics`
Get lyrics of the currently playing song.

> `.skip` / `.next`
Skip the current track.

> `.pause` / `.resume`
Pause or Resume playback.

> `.mstop`
Stop playback and clear the queue.

> `.loop [off|track|queue]`
Set or cycle music loop mode.

> `.queue`
Show the queue.
"""
