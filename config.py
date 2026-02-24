from typing import List, Optional

# Get this both from https://my.telegram.org/. Account login required.
API_ID: str | int = "10187126"
API_HASH: str = "ff197c0d23d7fe54c89b44ed092c1752"

# Get from https://telegram.tools
SESSION: str = "" # Example: "sessionqwertyuiopasdfghjkl..."
BOT_TOKEN: str = "" # Get from https://t.me/BotFather

# --- Optional ---
DB_URL: Optional[str] = "" # PostgreSQL URL. Optional it will fallback to SQLite if not provided.
OtherSessions: Optional[List[str]] = [] # Example: ["session1", "session2", ...] (High performance & memory usage)
PREFIX: List[str] = [".","~","$","^"]
GEMINI_API_KEY: Optional[str] = "" # Get it from https://aistudio.google.com/app/api-keys

# No need to change (almost all time)
DazzerBot: str = "@Dazzerbot" # This bot allows us to download songs
LRCLIB: str = "https://lrclib.net/" # This API allows us to get lyrics of songs

""" Tip(s):
* Pyrogram session(s) are only allowed.
* You can use Bot's session in BOT_TOKEN var. to avoid login errors.
* Never share your session with anyone. They can hack your account easily."""
# Created by: @DevsBase & @Otazuki
# Best userbot in Telegram!