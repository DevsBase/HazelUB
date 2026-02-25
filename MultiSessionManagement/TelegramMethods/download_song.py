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

async def get_audio_duration(file_path: str) -> int:
    """Get the duration of an audio file in seconds using ``ffprobe``.

    Runs ``ffprobe`` in a background thread (via :func:`asyncio.to_thread`) so
    the event loop is never blocked. If the probe fails for any reason (e.g.
    ``ffprobe`` is not installed, the file is corrupt, or the path is invalid),
    the function silently returns ``0`` instead of raising.

    Args:
        file_path (str): Absolute or relative path to the audio file to probe.

    Returns:
        int: Duration of the audio in whole seconds, or ``0`` if the duration
        could not be determined.
    """
    try:
        cmd = [
            'ffprobe', 
            '-v', 'error', 
            '-show_entries', 'format=duration', 
            '-of', 'default=noprint_wrappers=1:nokey=1', 
            file_path
        ]
        result = await asyncio.to_thread(subprocess.run, cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return int(float(result.stdout.strip()))
    except Exception as e:
        logging.debug(e)
        return 0

class DownloadSong:
    """Mixin class that adds song-downloading capability to the ``Telegram`` class.

    Leverages the ``@DazzerBot`` inline bot on Telegram to search for and
    download audio tracks. Downloaded media is saved locally as an MP3 file
    (video results are automatically converted using ``ffmpeg``).
    """

    async def download_song(self: "MultiSessionManagement.telegram.Telegram", query: str, client: pyrogram.Client) -> dict | None: # type: ignore
        """Search for and download a song via the DazzerBot inline bot.

        The method performs the following steps:

        1. Sends an inline query to ``@DazzerBot`` with the given *query*.
        2. Forwards the first inline result to the bot's own chat.
        3. Polls the chat (up to ~37 s) until the bot replies with a media
           message (audio, video, or voice).
        4. Downloads the media to a uniquely named temporary file.
        5. If the media is a video, converts it to MP3 using ``ffmpeg`` and
           removes the original video file.
        6. Returns a dictionary containing the file path and metadata.

        Args:
            query (str): The search query string (e.g. song title or
                ``"artist - title"``).
            client (pyrogram.Client): The Pyrogram client session to use
                for making the inline query and downloading the media.

        Returns:
            dict | None: A dictionary with the following keys on success, or
            ``None`` if no inline results were found:

            - **path** (*str*) – Local filesystem path to the downloaded MP3.
            - **title** (*str*) – Track title extracted from the media
              metadata, or ``"Unknown Title"`` as a fallback.
            - **performer** (*str*) – Artist / performer name, or
              ``"Unknown Artist"``.
            - **duration** (*int*) – Track duration in seconds.
            - **file_name** (*str*) – Base filename of the downloaded file.

        Raises:
            TimeoutError: If ``@DazzerBot`` does not respond with a media
                message within the polling window (~37 seconds).

        Note:
            Both ``ffprobe`` and ``ffmpeg`` must be available on ``$PATH``
            for duration detection and video-to-audio conversion to work.
        """
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
                        await asyncio.to_thread(subprocess.run, cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        if os.path.exists(temp_path): os.remove(temp_path)
                    except Exception as e:
                        logger.error(f"Video conversion failed: {e}")
                
                duration = getattr(media, 'duration', 0)
                if duration == 0:
                    duration = await get_audio_duration(final_path)

                return {
                    "path": final_path,
                    "title": getattr(media, 'title', None) or getattr(media, 'file_name', None) or "Unknown Title",
                    "performer": getattr(media, 'performer', "Unknown Artist"),
                    "duration": duration,
                    "file_name": os.path.basename(final_path)
                }
            await asyncio.sleep(1.5)
        raise TimeoutError("DazzerBot doesn't give media file.")