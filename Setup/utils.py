import logging
import os
import subprocess
import sys
from dataclasses import dataclass
from typing import List, Any

import config

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class HazelConfig:
    BOT_TOKEN: str
    API_ID: str
    API_HASH: str
    SESSION: str
    DB_URL: str
    OtherSessions: List[str]
    PREFIX: List[str]
    GEMINI_API_KEY: str


def clear() -> None:
    """Clear terminal screen."""
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        pass


def signal_handler(signum: int, __) -> None:
    """Handle termination signals."""
    logger.info("Stop signal received (%s). Stopping HazelUB...", signum)
    os._exit(0)


def install_requirements() -> int | str:
    """Ensure pip exists and install requirements."""
    subprocess.run(
        [sys.executable, "-m", "ensurepip"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-U", "-r", "requirements.txt"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        return 0

    return result.stderr


def _ask_missing(key: str) -> str:
    """Ask user interactively for missing config value."""
    try:
        value: str = input(f"Cannot find {key}. Please enter: ")
    except EOFError:
        raise SystemExit(
            f"Setup Failed: {key} is required but not found in config.py or env."
        )

    if len(value) < 3:
        print(f"Please enter a valid {key}")
        return _ask_missing(key)

    return value


def _resolve(key: str, default: Any = None) -> Any:
    """Resolve config value from config module or environment."""
    value = getattr(config, key, None) or os.getenv(key)

    if value:
        return value

    if default is not None:
        return default

    return _ask_missing(key)


def load_config() -> HazelConfig:
    """Load configuration."""
    BOT_TOKEN: str = _resolve("BOT_TOKEN")
    API_ID: str = _resolve("API_ID")
    API_HASH: str = _resolve("API_HASH")
    SESSION: str = _resolve("SESSION")

    DB_URL: str = _resolve("DB_URL", "")

    other_sessions_env: str = os.getenv("OtherSessions", "")
    OtherSessions: List[str] = config.OtherSessions or (
        other_sessions_env.split(",") if other_sessions_env else []
    )

    prefix_env: str = os.getenv("PREFIX", "")
    PREFIX: List[str] = list(config.PREFIX) or (
        prefix_env.split(",") if prefix_env else []
    )

    GEMINI_API_KEY: str = _resolve("GEMINI_API_KEY", "")

    return HazelConfig(
        BOT_TOKEN=BOT_TOKEN,
        API_ID=API_ID,
        API_HASH=API_HASH,
        SESSION=SESSION,
        DB_URL=DB_URL,
        OtherSessions=OtherSessions,
        PREFIX=PREFIX,
        GEMINI_API_KEY=GEMINI_API_KEY,
    )


def startup_popup():
    """Show a desktop notification indicating that HazelUB has started.

    Uses :mod:`plyer` for cross-platform notifications.
    """
    try:
        from plyer import notification
    except: return

    try:
        notification.notify(
            title="HazelUB",
            message="HazelUB has started successfully!",
            timeout=7
        ) # type: ignore
    except: pass