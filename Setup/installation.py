import Hazel
import os
from logging import getLogger
from restart import restart
from typing import TYPE_CHECKING, Tuple
from .utils import install_requirements, load_config, clear
from dotenv import load_dotenv

if TYPE_CHECKING:
    from Database.mongo_client import MongoClient
    from Database.redis_client import RedisClient
else:
    MongoClient = None
    RedisClient = None

logger = getLogger(__name__)

async def main() -> Tuple[MongoClient, tuple]:
    clear()
    print(
        "HazelUB is now booting...\n"
        "* If this is the first boot required packages may install.\n"
        f"Version: {Hazel.__version__}"
    )
    
    try: # Checking once if essential packages are installed.
        from motor.motor_asyncio import AsyncIOMotorClient
        from redis import asyncio as redis
        from art import text2art
        from pyrogram.client import Client
        from google import genai
    except ImportError:
        logger.critical("ImportError, Installing required packages...")
        install_status = install_requirements()
        if install_status == 0:
            logger.info("Packages installed successfully. Restarting...")
            restart()
        else:
            raise SystemExit(f"Setup Failed: Could not install required packages: {install_status}")
    
    from Database.mongo_client import MongoClient
    from Database.redis_client import RedisClient

    load_dotenv()
    config = load_config()
    
    # Init Mongo
    db = MongoClient(config[4])
    await db.init()
    Hazel.SQLClient = db 

    # Init Redis
    redis_url = config[5]
    if redis_url:
        Hazel.Redis = RedisClient(redis_url)

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