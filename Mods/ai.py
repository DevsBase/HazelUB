from google import genai
from pyrogram import filters, Client
from pyrogram.types import Message
from Hazel import Tele
import logging
import os
import asyncio

logger = logging.getLogger("Mods.ai")

AI_SESSIONS = {}

def get_ai_session(user_id, api_key):
    if user_id in AI_SESSIONS:
        return AI_SESSIONS[user_id]

    client = genai.Client(api_key=api_key)

    # Use currently supported model
    session = client.chats.create(
        model="gemini-1.5-flash"
    )

    AI_SESSIONS[user_id] = session
    return session


@Tele.on_message(filters.command("ai") & filters.me)
async def ai_cmd(c: Client, m: Message):

    import config
    api_key = config.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")

    if not api_key:
        return await m.edit("**GEMINI_API_KEY** is not found in config.py or env.")

    if len(m.command) < 2:
        return await m.edit("Usage: `.ai <your question>`")

    query = m.text.split(None, 1)[1]
    await m.edit("🔍 **Thinking...**")

    try:
        session = get_ai_session(c.me.id, api_key) # type: ignore

        response = await asyncio.to_thread(
            session.send_message,
            query
        )

        full_text = response.text

        if full_text and len(full_text) > 4000:
            full_text = full_text[:4000] + "..."

        await m.edit(f"🤖 **AI:**\n\n{full_text}")

    except Exception as e:
        logger.error(f"Gemini AI Error: {e}")
        await m.edit(f"❌ **Error:**\n`{e}`")


@Tele.on_message(filters.command("aiclr") & filters.me)
async def ai_clear(c: Client, m: Message):
    uid = c.me.id # type: ignore

    if uid in AI_SESSIONS:
        AI_SESSIONS.pop(uid)
        await m.edit("✅ **AI Chat History Cleared.**")
    else:
        await m.edit("ℹ️ **No active AI session to clear.**")


MOD_NAME = "AI"
MOD_HELP = """**Usage:**
> .ai <query> - Talk to Gemini AI
> .aiclr - Clear chat history for AI"""
