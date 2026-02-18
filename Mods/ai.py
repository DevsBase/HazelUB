import google.generativeai as genai
from pyrogram import filters, Client
from pyrogram.types import Message
from Hazel import Tele
import logging
import os

logger = logging.getLogger("Mods.ai")

# Dictionary to store chat sessions per user
# Key: user_id, Value: ChatSession object
AI_SESSIONS = {}

def get_ai_session(user_id, api_key):
    if user_id in AI_SESSIONS:
        return AI_SESSIONS[user_id]
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    session = model.start_chat(history=[])
    AI_SESSIONS[user_id] = session
    return session

@Tele.on_message(filters.command("ai") & filters.me)
async def ai_cmd(c: Client, m: Message):
    # Try to get API key from config/env
    import config
    api_key = config.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        return await m.edit("❌ **GEMINI_API_KEY** not found in config.py or environment variables.")

    if len(m.command) < 2:
        return await m.edit("Usage: `.ai <your question>`")

    query = m.text.split(None, 1)[1]
    await m.edit("🔍 **Thinking...**")

    try:
        session = get_ai_session(c.me.id, api_key) # type: ignore
        response = await asyncio.to_thread(session.send_message, query)
        
        # Split response if too long
        full_text = response.text
        if len(full_text) > 4000:
            # For simplicity, we just truncate or tell them to check logs, 
            # but ideally we split into multiple messages.
            # Truncating for now to avoid flood
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

import asyncio # Needed for to_thread

MOD_NAME = "AI"
MOD_HELP = """**Usage:**
> .ai <query> - Talk to Gemini AI
> .aiclr - Clear chat history for AI"""
