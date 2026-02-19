import MultiSessionManagement.telegram
import pyrogram
import asyncio
import config

class DownloadSong:
    async def download_song(self: "MultiSessionManagement.telegram.Telegram", query: str, client: pyrogram.Client) -> str | None: # type: ignore
        results = await client.get_inline_bot_results(config.DazzerBot, query)
        if not results:
            return None
        m = await client.send_inline_bot_result(
            self.bot.me.username, # type: ignore
            results.query_id,
            results.results[0].id
        )
        await asyncio.sleep(3)
        for _ in range(1, 20):
            _m = await client.get_messages(m.chat.id, m.id)
            if hasattr(_m, 'audio') and getattr(_m, 'audio'):
                path = str(await client.download_media(_m)) # type: ignore
                return path
            await asyncio.sleep(1.5)
        raise TimeoutError("DazzerBot doesn't gave audio file.")


