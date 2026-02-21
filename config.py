API_ID = "10187126"
API_HASH = "ff197c0d23d7fe54c89b44ed092c1752"
SESSION = "" # Example: "sessionqwertyuiopasdfghjkl..."
BOT_TOKEN = ""
DB_URL = "" # PostgreSQL URL
OtherSessions = [] # Example: ["session1", "session2", ...]
PREFIX = [".","~","$","^"]
GEMINI_API_KEY = "" # Get it from https://aistudio.google.com/app/api-keys

# No need to change (almost all time)
import time
DazzerBot = "@Dazzerbot" # This bot allows us to download songs
START_TIME: float = time.time()

"""
* Pyrogram session(s) are only allowed.
* You can use Bot's session in BOT_TOKEN var. to avoid login errors.
"""