import numpy as np
from typing import Dict, List, cast

from Hazel import Tele

from pyrogram.client import Client
from pyrogram.types import Message
from pyrogram import filters

from pytgcalls import PyTgCalls
from pytgcalls import filters as call_filter
from pytgcalls.types import (
    Device,
    Direction,
    ExternalMedia,
    RecordStream,
    MediaStream,
)
from pytgcalls.types.raw import AudioParameters
from pytgcalls.types.stream import StreamFrames


data: Dict[int, Dict[str, List[int]]] = {}


@Tele.on_message(filters.command(["bridge", "sbridge"]), sudo=True)
async def bridge_func(app: Client, m: Message) -> None:
    me = app.me
    user_id: int = me.id  # type: ignore

    command: List[str] = m.command or []

    if not command:
        return

    # Stop bridging
    if command[0] == "sbridge":

        if user_id not in data:
            await m.reply("Bridging is not active.")
            return

        _callpy = Tele.getClientPyTgCalls(app)
        if isinstance(_callpy, PyTgCalls):
            call_py: PyTgCalls = _callpy

        chat_ids: List[int] = data[user_id]["chat_ids"]

        for chat_id in chat_ids:
            try:
                await call_py.leave_call(chat_id)
            except Exception:
                pass

        del data[user_id]
        await m.reply("Stopped bridging.")
        return

    # Already running
    if user_id in data:
        await m.reply(
            "Already running somewhere. Use .sbridge to stop it first."
        )
        return

    if len(command) < 2:
        await m.reply("Okay, I'll bridge. But from where?")
        return

    try:
        cmd = m.command[1] if m.command else ""
        try: cmd = int(cmd)
        except: ...
        target_chat = await app.get_chat(cmd)
    except Exception:
        await m.reply("Cannot find the chat.")
        return

    if m.chat is None or m.chat.id is None:
        return

    if target_chat.id is None:
        await m.reply("Invalid target chat.")
        return

    _callpy = Tele.getClientPyTgCalls(app)
    if isinstance(_callpy, PyTgCalls):
        call_py: PyTgCalls = _callpy

    audio_parameters = AudioParameters(
        bitrate=48000,
        channels=2,
    )

    chat_ids: List[int] = [
        int(m.chat.id),
        int(target_chat.id),
    ]

    try:
        for chat_id in chat_ids:
            await call_py.play(
                chat_id,
                MediaStream(
                    ExternalMedia.AUDIO,
                    audio_parameters,
                ),
            )

            await call_py.record(
                chat_id,
                RecordStream(
                    True,
                    audio_parameters,
                ),
            )

    except Exception as e:
        await m.reply(f"Failed to bridge: {e}")
        return

    data[user_id] = {"chat_ids": chat_ids}

    await m.reply(
        "Bridging started! 🔊\n"
        "Both chats can now hear each other.\n"
        "Use .sbridge to stop bridging."
    )


@Tele.on_update(
    call_filter.stream_frame(
        Direction.INCOMING,
        Device.MICROPHONE,
    )
)
async def audio_data(
    call_py: PyTgCalls,
    update: StreamFrames,
) -> None:

    app = cast(Client, call_py.mtproto_client)

    me = app.me
    user_id: int = me.id # type: ignore

    if user_id not in data:
        return

    chat_ids: List[int] = data[user_id]["chat_ids"]

    if update.chat_id not in chat_ids:
        return

    forward_chat_ids: List[int] = [
        x for x in chat_ids if x != update.chat_id
    ]

    if not update.frames:
        return

    first_frame = update.frames[0]

    if first_frame.frame is None:
        return

    mixed_output = np.zeros(
        len(first_frame.frame) // 2,
        dtype=np.int16,
    )

    for frame_data in update.frames:

        if frame_data.frame is None:
            continue

        source_samples = np.frombuffer(
            frame_data.frame,
            dtype=np.int16,
        )

        mixed_output[: len(source_samples)] += source_samples

    mixed_output //= max(len(update.frames), 1)
    mixed_output = np.clip(
        mixed_output,
        -32768,
        32767,
    )

    output_bytes: bytes = mixed_output.tobytes()

    for f_chat_id in forward_chat_ids:
        try:
            await call_py.send_frame(
                f_chat_id,
                Device.MICROPHONE,
                output_bytes,
            )
        except Exception:
            pass


MOD_NAME = "Bridge"
MOD_HELP = (
    "> .bridge <username/link/id> - Bridge two voice chats.\n"
    "> .sbridge - Stop bridging."
)