import time
from logging import getLogger
from typing import TYPE_CHECKING, Tuple

import Hazel
from restart import restart

from .utils import HazelConfig, clear, install_requirements, load_config

if TYPE_CHECKING:
    from Database.client import DBClient
else:
    DBClient = None

logger = getLogger(__name__)

async def main() -> Tuple[DBClient, HazelConfig]:
    """Run the installation and configuration sequence for HazelUB."""
    clear()
    print(
        "HazelUB is now booting...\n"
        "* If this is the first boot required packages may install.\n"
        f"Version: {Hazel.__version__}"
    )
    try:
        import ensurepip
        ensurepip.bootstrap()
    except ImportError:
        pass
    
    try: 
        # Checking once if essential packages are installed.
        import aiosqlite
        import art
        import asyncpg
        import cachetools
        import sqlalchemy
        import pytgcalls
        import requests
        from dotenv import load_dotenv
        from pyrogram.client import Client
    except ImportError:
        logger.info("ImportError, Installing required packages...")
        install_status = install_requirements()
        if install_status == 0:
            logger.info("Packages installed successfully. Restarting...")
            time.sleep(4)
            restart()
        else:
            raise SystemExit(f"Setup Failed: Could not install required packages: {install_status}")
    
    from Database.client import DBClient

    load_dotenv()
    config = load_config()
    db = DBClient(config.DB_URL)
    await db.init()
    Hazel.SQLClient = db # Override
    Hazel.sudoers = await db.get_all_sudoers_map() # Override
    return (db, config)