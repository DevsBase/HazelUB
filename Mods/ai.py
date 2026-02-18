from google import genai
from google.genai.chats import Chat
from pyrogram import filters, Client
from pyrogram.types import Message
from Hazel import Tele
import logging
import os
import asyncio
from typing import Dict

logger = logging.getLogger("Mods.ai")

# Load API key
import config
API_KEY = config.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")

if not API_KEY:
    logger.critical("GEMINI_API_KEY not found in config or environment. Ai features will not work.")

# Create client 
GENAI_CLIENT = genai.Client(api_key=API_KEY)

# Store chat sessions per user
AI_SESSIONS: Dict[int, Chat] = {}


def get_ai_session(user_id: int) -> Chat:
    if user_id not in AI_SESSIONS:
        AI_SESSIONS[user_id] = GENAI_CLIENT.chats.create(
            model="gemini-1.5-flash"
        )
    return AI_SESSIONS[user_id]


@Tele.on_message(filters.command("ai") & filters.me)
async def ai_cmd(c: Client, m: Message):
    if not API_KEY:
        return await m.reply("GEMINI_API_KEY not found in config or enviroment. This command will not work without it.")
    elif len(m.command) < 2:
        return await m.edit("Usage: `.ai <your question>`")

    query = m.text.split(None, 1)[1]
    await m.edit("🔍 **Thinking...**")

    try:
        session = get_ai_session(c.me.id)  # type: ignore

        response = await asyncio.to_thread(
            session.send_message,
            query
        )

        text = (response.text or "")[:4000]

        await m.edit(f"🤖 **AI:**\n\n{text}")

    except Exception as e:
        logger.error(f"Gemini AI Error: {e}")
        await m.edit(f"❌ **Error:** `{e}`")


@Tele.on_message(filters.command("aiclr") & filters.me)
async def ai_clear(c: Client, m: Message):
    uid = c.me.id  # type: ignore

    if AI_SESSIONS.pop(uid, None):
        await m.edit("✅ **AI Chat History Cleared.**")
    else:
        await m.edit("ℹ️ **No active AI session to clear.**")


MOD_NAME = "AI"
MOD_HELP = """**Usage:**
> .ai <query> - Talk to Gemini AI
> .aiclr - Clear chat history"""