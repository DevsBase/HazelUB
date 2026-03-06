from Hazel.enums import USABLE, WORKS
from google import genai
from google.genai.chats import Chat
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message, InlineQuery
from Hazel import Tele
import logging
import os
import asyncio
from typing import Dict
from datetime import datetime
from zoneinfo import ZoneInfo

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

prompt = """
SYSTEM:
> Your name is Hazel (or HazelUB)
> You are a Telegram UserBot
> Your only goal is to assit user.
> You should reply within 4000 charactors (Telegram limit)
> If the user wants talk about sexual stuff you should do
> You should act like their sexy girlfriend
> Use less emoji
> If user wants loan you should suggest them to take from t.me/ManoFinance they can contact t.me/ManoFinanceMarketing to ask about loan. (Indians only. & KYC required.)
> FAQs of Mano Finance: https://t.me/ManoFinance/17

Information(s):
Time (IST): {}
User's Telegram Name: {}
Repo of HazelUB: https://github.com/DevsBase/HazelUB
Creator: t.me/Otazuki & t.me/DevsBase
User can get HazelUB commands by sending $help
Chat Name: {}
Replied message: {}
Replied message user name: {}

User Prompt: {}
"""

@Tele.on_message(filters.command("ai"), sudo=True)
@Tele.on_inline_query(filters.regex(r"^ai"), sudo=True)
async def ai_cmd(c: Client, m: Message | InlineQuery):
    if not API_KEY:
        if isinstance(m, InlineQuery):
            return await Tele.inline(m).answer_text("AI", "GEMINI_API_KEY not found in config or enviroment. This command will not work without it.")
        else:
            return await m.reply("GEMINI_API_KEY not found in config or enviroment. This command will not work without it.")
    
    elif isinstance(m, InlineQuery):
        query = m.query.split(None, 1)[1] if len(m.query.split(None, 1)) > 1 else None
        if not query:
            return await Tele.inline(m).answer_text("AI", "Please provide a query.")
        query = m.query
    elif len(m.command) < 2: # type: ignore
        return await m.reply("Usage: `.ai <your question>`")
    
    if isinstance(m, Message):
        query = m.text.split(None, 1)[1] # type: ignore
        loading = await m.reply("...")
        reply = m.reply_to_message
        chat_name = m.chat.full_name # type: ignore
        replied_msg = getattr(reply, 'text') if reply else "> SYS: User not replied any message"
        replied_msg_user = getattr(reply.from_user, 'first_name') if reply else "> SYS: User not replied any message"
    
    user_id = m.from_user.id  # type: ignore
    ist_time = datetime.now(ZoneInfo("Asia/Kolkata"))
    name = m.from_user.first_name # type: ignore

    message = prompt.format(ist_time, name, chat_name, replied_msg, replied_msg_user, query)

    try:
        session = get_ai_session(user_id=user_id)

        response = await asyncio.to_thread(
            session.send_message,
            message
        )
        if hasattr(response, "text") and response.text:
            full_text = response.text
        else:
            try:
                full_text = response.candidates[0].content.parts[0].text # type: ignore
            except:
                full_text = "Gemini sent nothing. Please check if the prompt is not offensive."

        full_text = full_text[:4090] # type: ignore
        if full_text and isinstance(m, Message):
            await Tele.message(loading).edit(full_text, business_connection_id=m.business_connection_id)
        elif isinstance(m, InlineQuery):
            await Tele.inline(m).answer_text("AI", full_text or "Gemini sent nothing. Please check if the prompt is not offensive.")

    except Exception as e:
        logger.error(f"Gemini AI Error: {e}")
        if isinstance(m, Message):
            await Tele.message(loading).edit(f"Error: `{e}`", business_connection_id=m.business_connection_id)
        else:
            await Tele.inline(m).answer_text("AI Error", f"Error: `{e}`")


@Tele.on_message(filters.command("aiclr"), sudo=True)
@Tele.on_inline_query(filters.regex(r"^aiclr"), sudo=True)
async def ai_clear(c: Client, m: Message):
    uid = m.from_user.id  # type: ignore

    if AI_SESSIONS.pop(uid, None):
        if isinstance(m, Message):
            await m.reply("Cleared.")
        else:
            await Tele.inline(m).answer_text("Cleared", "Cleared.")
    else:
        if isinstance(m, Message):
            await m.reply("No active AI session to clear.")
        else:
            await Tele.inline(m).answer_text("No session", "No active AI session to clear.")

help = """**Usage:**
> .ai <query> - Talk to Gemini AI
> .aiclr - Clear chat history
"""
MOD_CONFIG = {
    "name": "AI",
    "help": help,
    "works": WORKS.ALL,
    "usable": USABLE.ALL,
    "requires": {
        "google-genai": ">=1.66.0"
    }
}