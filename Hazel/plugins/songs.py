from Hazel import HANDLER, on_message
from pyrogram import filters
import os
import requests
from youtube_search import YoutubeSearch
from yt_dlp import YoutubeDL

async def download_youtube(query=None, media_type="song", link=""):
  is_video = media_type == "video"
  if not query and not link:
    raise ValueError("Query or link argument must provied.")
  try:
    if link:
      with YoutubeDL({'quiet': True, 'cookiefile': 'cookies.txt'}) as ydl:
        info = ydl.extract_info(link, download=False)
        title = info.get("title", "Unknown Title")
        thumbnail = info.get("thumbnail")
        duration = info.get("duration", 0)
    else:
      results = YoutubeSearch(query, max_results=1).to_dict()
      if not results:
        raise Exception("No results.")
      link = f"https://youtube.com{results[0]['url_suffix']}"
      title = results[0]["title"]
      thumbnail = results[0]["thumbnails"][0]
      duration = results[0]["duration"]
    thumb_name = f"{title.replace('/', '_')}.jpg"
    if thumbnail:
      thumb = requests.get(thumbnail, allow_redirects=True)
      if thumb.status_code == 200:
        with open(thumb_name, "wb") as f:
          f.write(thumb.content)
      else: thumb_name = None
    else: thumb_name = None
    ydl_opts = {
      "format": "best" if is_video else "bestaudio[ext=m4a]",
      "cookiefile": "cookies.txt",
      "outtmpl": f"downloads/%(title)s.%(ext)s"
    }
    with YoutubeDL(ydl_opts) as ydl:
      info_dict = ydl.extract_info(link, download=True)
      media_file = ydl.prepare_filename(info_dict)
    secmul, dur, dur_arr = 1, 0, str(duration).split(":")
    for i in range(len(dur_arr) - 1, -1, -1):
      dur += int(float(dur_arr[i])) * secmul
      secmul *= 60
    return media_file, thumb_name, dur
  except Exception as e:
    raise RuntimeError(f"Download failed: {e}")

@on_message(filters.command(["song", "video"], prefixes=HANDLER) & filters.me)
async def youtube(app, message):
  if len(message.text.split()) < 2:
    return await message.reply("Provide a song/video name or YouTube link.")
  query = " ".join(message.command[1:])
  media_type = message.command[0].lower()
  msg = await message.reply("📥 Downloading...")
  media_file, thumb_name, duration_or_error = await download_youtube(query, media_type)
  if not media_file:
    return await msg.edit(f"Error: {duration_or_error}")
  await msg.edit("📤 Uploading...")
  if media_type == "video":
    await message.reply_video(
      media_file,
      thumb=thumb_name,
      caption=os.path.basename(media_file),
      duration=duration_or_error
    )
  else:
    await message.reply_audio(
      media_file,
      thumb=thumb_name,
      title=os.path.basename(media_file),
      caption=os.path.basename(media_file),
      duration=duration_or_error
    )
  await msg.delete()
  if os.path.exists(media_file):
    os.remove(media_file)
  if thumb_name and os.path.exists(thumb_name):
    os.remove(thumb_name)