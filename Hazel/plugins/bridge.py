import numpy as np
from pytgcalls import filters as call_filter
from pytgcalls.types import Device, Direction, ExternalMedia, RecordStream, MediaStream, StreamFrames
from pytgcalls.types.raw import AudioParameters
from Hazel import on_message, HANDLER, on_update
from pyrogram import filters

data = {}

@on_message(filters.command(['bridge','sbridge'],prefixes=HANDLER) & filters.me)
async def bridge_func(app,m):
  global data
  if (m.command[0] == "sbridge"):
    if not (data.get(app.me.id)):
      return await m.reply("Bridging is not active.")
    chat_ids = data[app.me.id].get("chat_ids",[])
    for chatid in chat_ids:
      await app.pytgcalls.leave_call(chatid)
    del data[app.me.id]
    return await m.reply("Stopped bridging.")
  if data.get(app.me.id):
    return await m.reply("Already this command is running somewhere. Please use .sbridge to end it.")
  elif len(m.command) < 2:
    return await m.reply("Okay, I'll bridge. But from where?")
  chat = m.command[1]
  try: chat = await app.get_chat(chat)
  except: return await m.reply("Cannot find the chat.")
  call_py = app.pytgcalls
  AUDIO_PARAMETERS = AudioParameters(bitrate=48000, channels=2)
  chat_ids = [m.chat.id,chat.id]
  try:
    for chat_id in chat_ids:
      await call_py.play(chat_id,MediaStream(ExternalMedia.AUDIO,AUDIO_PARAMETERS))
      await call_py.record(chat_id,RecordStream(True,AUDIO_PARAMETERS))
  except Exception as e:
    return await m.reply(f"Failed to bridge: {e}")
  data[app.me.id] = {"chat_ids": chat_ids}
  await m.reply(f"Bridging started! Now both chats are connected, so both chats can hear other chat's audio. Use .sbridge to stop bridging.")
  
@on_update(call_filter.stream_frame(Direction.INCOMING,Device.MICROPHONE))
async def audio_data(call_py, update):
  app = call_py.mtproto_client
  if (app.me.id in data and update.chat_id in data[app.me.id]["chat_ids"]):
    chat_ids = data[app.me.id]["chat_ids"]
    forward_chat_ids = [x for x in chat_ids if x != update.chat_id]
    mixed_output = np.zeros(
      len(update.frames[0].frame) // 2,
      dtype=np.int16,
    )
    for frame_data in update.frames:
      source_samples = np.frombuffer(frame_data.frame, dtype=np.int16)
      mixed_output[:len(source_samples)] += source_samples
    mixed_output //= max(len(update.frames), 1)
    mixed_output = np.clip(mixed_output, -32768, 32767)
    for f_chat_id in forward_chat_ids:
      await call_py.send_frame(f_chat_id,Device.MICROPHONE,mixed_output.tobytes())
      
MOD_NAME = "Bridge"      
MOD_HELP = ".bridge <username/link/id> - To bridge two voice chats."