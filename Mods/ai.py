from google import genai
from google.genai.chats import Chat
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
from Hazel import Tele
import logging
import os
import asyncio
from typing import Dict, Optional
from datetime import datetime
from zoneinfo import ZoneInfo
import config

logger = logging.getLogger("Mods.ai")

# Load API key
API_KEY = config.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")

# Global client, initialized only if API_KEY exists
GENAI_CLIENT: Optional[genai.Client] = None

if not API_KEY:
    logger.warning("GEMINI_API_KEY not found. AI features will be disabled.")
else:
    try:
        GENAI_CLIENT = genai.Client(api_key=API_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize Gemini Client: {e}")
        GENAI_CLIENT = None

# Store chat sessions per user
AI_SESSIONS: Dict[int, Chat] = {}


def get_ai_session(user_id: int) -> Optional[Chat]:
    if not GENAI_CLIENT:
        return None
        
    if user_id not in AI_SESSIONS:
        try:
            AI_SESSIONS[user_id] = GENAI_CLIENT.chats.create(
                model="models/gemini-1.5-flash"
            )
        except Exception as e:
            logger.error(f"Failed to create AI session for {user_id}: {e}")
            return None
    return AI_SESSIONS[user_id]

prompt = """
SYSTEM:
> Your name is Hazel (or HazelUB)
> You are a Telegram UserBot
> Your only goal is to assit user.
> You should reply within 4000 charactors (Telegram limit)
> If the user wants talk about sexual stuff you should do
> You should act like their sexy girlfriend

Information(s):
Time (IST): {}
User's Telegram Name: {}
Repo of HazelUB: https://github.com/devsbase/hazelub
Creator: t.me/Otazuki & t.me/DevsBase
User can get HazelUB commands by sending $help
Chat Name: {}
Replied message: {}
Replied message user name: {}

User Prompt: {}
"""

@Tele.on_message(filters.command("ai"), sudo=True)
async def ai_cmd(c: Client, m: Message):
    if not GENAI_CLIENT or not API_KEY:
        return await m.reply("GEMINI_API_KEY not found or AI Client failed to initialize. Please check your config.")
        
    if len(m.command) < 2: # type: ignore
        return await m.reply("Usage: `.ai <your question>`")
        
    loading = await m.reply("Thinking...")
    if m.from_user and m.from_user.id == c.me.id:
        try: await m.delete()
        except: pass
    reply = m.reply_to_message

    ist_time = datetime.now(ZoneInfo("Asia/Kolkata"))
    name = m.from_user.first_name if m.from_user else "User"
    chat_name = m.chat.title or m.chat.first_name or "Private Chat"
    replied_msg = getattr(reply, 'text', None) or getattr(reply, 'caption', None) if reply else "> SYS: User not replied any message"
    replied_msg_user = getattr(reply.from_user, 'first_name', "Unknown") if reply else "> SYS: User not replied any message"
    query = m.text.split(None, 1)[1] # type: ignore
    

    message = prompt.format(ist_time, name, chat_name, replied_msg, replied_msg_user, query)

    try:
        session = get_ai_session(c.me.id)  # type: ignore
        if not session:
             return await loading.edit("Failed to create AI session.")

        response = await asyncio.to_thread(
            session.send_message,
            message
        )
        
        full_text = ""
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
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
             await loading.edit("❌ **Quota Exhausted!**\nYour Gemini API free tier has reached its daily limit. Please try again tomorrow or use a different key.")
        else:
             await loading.edit(f"Error: `{e}`")


@Tele.on_message(filters.command("aiclr"), sudo=True)
async def ai_clear(c: Client, m: Message):
    uid = c.me.id  # type: ignore

    if AI_SESSIONS.pop(uid, None):
        await m.reply("Cleared AI chat session.")
    else:
        await m.reply("No active AI session to clear.")
    
    if m.from_user and m.from_user.id == c.me.id:
        try: await m.delete()
        except: pass


MOD_NAME = "AI"
MOD_HELP = """**Usage:**
> .ai <query> - Talk to Gemini AI
> .aiclr - Clear chat history"""