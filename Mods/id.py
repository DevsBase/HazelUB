from Hazel import Tele
import pyrogram

@Tele.on_message(pyrogram.filters.command("id"), sudo=True)
async def id_func(_, m: pyrogram.types.Message):
  reply = m.reply_to_message
  _reply = ""

  if not reply:
    no_reply = f"**Your ID**: `{m.from_user.id}`\n" # type: ignore
    no_reply += f"**Chat ID**: `{m.chat.id}`\n" # type: ignore
    no_reply += f"**Message ID**: `{m.id}`"
    await m.reply(text=(no_reply))
  if reply and reply.from_user:
    _reply += f"**Your ID**: `{m.from_user.id}`\n" # type: ignore
    _reply += f"**Replied User ID**: `{reply.from_user.id}`\n"
    _reply += f"**Chat ID**: `{m.chat.id}`\n" # type: ignore
    _reply += f"**Replied Message ID**: `{reply.id}`\n"
  if reply and reply.sender_chat:
    _reply += f"\n**Channel ID**: `{reply.sender_chat.id}`\n"
  if reply and reply.sticker:
    _reply += f"**Sticker ID**: `{reply.sticker.file_id}`"
  elif reply and reply.animation:
    _reply += f"**Animation ID**: `{reply.animation.file_id}`"
  elif reply and reply.document:
    _reply += f"**Document ID**: `{reply.document.file_id}`"
  elif reply and reply.audio:
    _reply += f"**Audio ID**: `{reply.audio.file_id}`"
  elif reply and reply.video:
    _reply += f"**Video ID**: `{reply.video.file_id}`"
  elif reply and reply.photo:
    _reply += f"**Photo ID**: `{reply.photo.file_id}`"
  if reply: await reply.reply(_reply)
  
MOD_NAME = "ID"
MOD_HELP = "> .id - reply someone or get current chat id."