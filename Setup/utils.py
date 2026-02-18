import subprocess
import asyncio
import logging
import config
import sys
import os 

logger = logging.getLogger(__name__)

def clear():
    try: os.system('cls' if os.name == 'nt' else 'clear')
    except: pass

def signal_handler(signum, __):
    logger.info(f"Stop signal received ({signum}). Stopping HazelUB...")
    os._exit(0)

def install_requirements():
    subprocess.run( # Install PIP if not available
        [sys.executable, "-m", "ensurepip"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    result = subprocess.run( # Install requirements.txt
        [sys.executable, "-m", "pip", "install", "-U", "-r", "requirements.txt"],
        capture_output=True,
        text=True
    )
    
    return result.returncode if result.returncode == 0 else result.stderr

    
def _ask_missing(key: str):
    try:
        value = input(f'Cannot find {key} in env or config.py. Please enter: ')
    except EOFError:
        raise SystemExit(f'Setup Failed: {key} is required and cannot found in config.py or env.')
    if len(value) < 3:
        print(f"Please enter valid {key}")
        return _ask_missing(key)

def load_config() -> tuple:
    BOT_TOKEN = config.BOT_TOKEN or os.getenv('BOT_TOKEN') or _ask_missing("BOT_TOKEN")
    API_ID = config.API_ID or os.getenv('API_ID') or _ask_missing("API_ID")
    API_HASH = config.API_HASH or os.getenv('API_HASH') or _ask_missing("API_HASH")
    SESSION = config.SESSION or os.getenv('SESSION') or _ask_missing("SESSION")
    DB_URL = config.DB_URL or os.getenv('DB_URL') or _ask_missing("DB_URL")
    # ---------- Optional ----------
    OtherSessions = config.OtherSessions or list(os.getenv('OtherSessions', []))
    PREFIX = list(config.PREFIX) or os.getenv('PREFIX', [])
    GEMINI_API_KEY = config.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY', '')
    return (BOT_TOKEN, API_ID, API_HASH, SESSION, DB_URL, OtherSessions, PREFIX, GEMINI_API_KEY)

def startup_popup():
    from plyer import notification

    try:
        notification.notify(
            title="HazelUB",
            message="HazelUB has started successfully!",
            timeout=7
        ) # type: ignore
    except: pass