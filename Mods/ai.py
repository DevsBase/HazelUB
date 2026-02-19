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
            model="models/gemini-2.5-flash"
        )
    return AI_SESSIONS[user_id]


@Tele.on_message(filters.command("ai") & filters.me)
async def ai_cmd(c: Client, m: Message):
    if not API_KEY:
        return await m.reply("GEMINI_API_KEY not found in config or enviroment. This command will not work without it.")
    elif len(m.command) < 2:
        return await m.edit("Usage: `.ai <your question>`")

    query = m.text.split(None, 1)[1]
    loading = await m.reply("...")

    try:
        session = get_ai_session(c.me.id)  # type: ignore

        response = await asyncio.to_thread(
            session.send_message,
            query
        )
        if hasattr(response, "text") and response.text:
            full_text = response.text
        else:
            try:
                full_text = response.candidates[0].content.parts[0].text # type: ignore
            except:
                full_text = "Gemini sent nothing. Please check if the prompt is not offensive."

        full_text = full_text[:4090] # type: ignore
        if full_text:
            await loading.edit(full_text)

    except Exception as e:
        logger.error(f"Gemini AI Error: {e}")
        await loading.edit(f"Error: `{e}`")


@Tele.on_message(filters.command("aiclr") & filters.me)
async def ai_clear(c: Client, m: Message):
    uid = c.me.id  # type: ignore

    if AI_SESSIONS.pop(uid, None):
        await m.edit("Cleared.")
    else:
        await m.edit("No active AI session to clear.")


MOD_NAME = "AI"
MOD_HELP = """**Usage:**
> .ai <query> - Talk to Gemini AI
> .aiclr - Clear chat history"""