import MultiSessionManagement.telegram
import pyrogram
import asyncio
import config
import os
import time
import random
import string
import subprocess
import logging

logger = logging.getLogger(__name__)

def get_audio_duration(file_path: str) -> int:
    """Helper to get audio duration using ffprobe."""
    try:
        cmd = [
            'ffprobe', 
            '-v', 'error', 
            '-show_entries', 'format=duration', 
            '-of', 'default=noprint_wrappers=1:nokey=1', 
            file_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return int(float(result.stdout.strip()))
    except Exception as e:
        logging.debug(e)
        return 0

class DownloadSong:
    async def download_song(self: "MultiSessionManagement.telegram.Telegram", query: str, client: pyrogram.Client) -> dict | None: # type: ignore
        results = await client.get_inline_bot_results(config.DazzerBot, query)
        if not results:
            return None
        
        m = await client.send_inline_bot_result(
            self.bot.me.username, # type: ignore
            results.query_id,
            results.results[0].id
        )
        
        await asyncio.sleep(2)
        for _ in range(1, 25):
            _m_raw = await client.get_messages(m.chat.id, m.id) # type: ignore
            if isinstance(_m_raw, list):
                _m = _m_raw[0]
            else:
                _m = _m_raw
            
            if not _m:
                await asyncio.sleep(1.5)
                continue

            media = getattr(_m, 'audio', None) or getattr(_m, 'video', None) or getattr(_m, 'voice', None)
            
            if media:
                # Generate a unique filename
                random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                unique_name = f"hazel_{int(time.time())}_{random_str}"
                
                # Check if it's a video that needs conversion
                is_video = hasattr(_m, 'video') and bool(_m.video)
                ext = ".mp4" if is_video else ".mp3"
                temp_path = str(await client.download_media(_m, file_name=unique_name + ext)) # type: ignore
                
                final_path = temp_path
                if is_video:
                    final_path = temp_path.replace(".mp4", ".mp3")
                    try:
                        cmd = ['ffmpeg', '-i', temp_path, '-vn', '-acodec', 'libmp3lame', '-q:a', '2', final_path, '-y']
                        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        if os.path.exists(temp_path): os.remove(temp_path)
                    except Exception as e:
                        logger.error(f"Video conversion failed: {e}")
                
                duration = getattr(media, 'duration', 0)
                if duration == 0:
                    duration = get_audio_duration(final_path)

                return {
                    "path": final_path,
                    "title": getattr(media, 'title', None) or getattr(media, 'file_name', None) or "Unknown Title",
                    "performer": getattr(media, 'performer', "Unknown Artist"),
                    "duration": duration,
                    "file_name": os.path.basename(final_path)
                }
            await asyncio.sleep(1.5)
        raise TimeoutError("DazzerBot doesn't give media file.")


