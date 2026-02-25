import Hazel
from logging import getLogger
from restart import restart
from typing import TYPE_CHECKING, Tuple
from .utils import install_requirements, load_config, clear

if TYPE_CHECKING:
    from Database.client import DBClient
else:
    DBClient = None

logger = getLogger(__name__)

async def main() -> Tuple[DBClient, tuple]:
    """Run the installation and configuration sequence for HazelUB.

    The function performs two checks:

    1. **Essential-package check** – imports critical dependencies
       (``dotenv``, ``sqlalchemy``, ``pyrogram``, etc.) and, if any
       are missing, installs them from ``requirements.txt`` and
       restarts the process.
    2. **First-time setup** – if the database ``installed`` flag is
       ``False``, installs/upgrades packages from ``requirements.txt``
       and marks the bot as installed.

    Between these checks the database engine is created, all tables
    are initialised, and the global ``Hazel.SQLClient`` /
    ``Hazel.sudoers`` references are populated.

    Returns:
        A tuple ``(db, config)`` where *db* is the initialised
        :class:`DBClient` and *config* is the loaded configuration
        tuple.
    """
    clear()
    print(
        "HazelUB is now booting...\n"
        "* If this is the first boot required packages may install.\n"
        f"Version: {Hazel.__version__}"
    )
    
    try: # Checking once if essential packages are installed.
        from dotenv import load_dotenv
        from sqlalchemy import create_engine
        from asyncpg import create_pool
        from aiosqlite import connect
        from art import text2art
        from pyrogram.client import Client
        from google import genai
        from googlesearch import search
    except ImportError:
        logger.critical("ImportError, Installing required packages...")
        install_status = install_requirements()
        if install_status == 0:
            logger.info("Packages installed successfully. Restarting...")
            restart()
        else:
            raise SystemExit(f"Setup Failed: Could not install required packages: {install_status}")
    
    from Database.client import DBClient

    load_dotenv()
    config = load_config()
    db = DBClient(config[4])
    await db.init()
    Hazel.SQLClient = db # Override SQLClient in Hazel.__init__
    Hazel.sudoers = await db.get_all_sudoers_map()

    is_installed = await db.is_installed()
    if not is_installed:
        logger.info("Installing required packages...")
        install_status = install_requirements()
        if install_status == 0:
            logger.info("Packages installed successfully.")
        else:
            raise SystemExit(f"Setup Failed: Could not install required packages: {install_status}")
        await db.set_installed(True)
    return (db, config)