import MultiSessionManagement.telegram
import pyrogram
import asyncio
import config
import os
import time
import random
import string

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
        for _ in range(1, 20):
            _m = await client.get_messages(m.chat.id, m.id) # type: ignore
            if hasattr(_m, 'audio') and getattr(_m, 'audio'):
                audio = getattr(_m, 'audio')
                
                # Generate a unique filename to avoid bugs mentioned by user
                random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                unique_name = f"hazel_{int(time.time())}_{random_str}.mp3"
                
                path = str(await client.download_media(_m, file_name=unique_name)) # type: ignore
                
                return {
                    "path": path,
                    "title": audio.title or "Unknown Title",
                    "performer": audio.performer or "Unknown Artist",
                    "duration": audio.duration or 0,
                    "file_name": unique_name
                }
            await asyncio.sleep(1.5)
        raise TimeoutError("DazzerBot doesn't give audio file.")


