import os
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv("API_ID", "10187126")
API_HASH = os.getenv("API_HASH", "ff197c0d23d7fe54c89b44ed092c1752")
SESSION = os.getenv("SESSION", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MONGO_URL = os.getenv("MONGO_URL", "")
REDIS_URL = os.getenv("REDIS_URL", "")
OtherSessions = os.getenv("OtherSessions", "").split()
PREFIX = os.getenv("PREFIX", ". ~ $ ^").split()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# No need to change (almost all time)
DazzerBot = "@Dazzerbot"