import os
import art
import Hazel
import asyncio 
import logging
import traceback
from pyrogram.sync import idle
from Database.client import DBClient
from MultiSessionManagement.telegram import Telegram
from signal import signal as signal_fn, SIGINT, SIGTERM, SIGABRT
from .utils import install_requirements, load_config, signal_handler, signal_handler, startup_popup


# Tasks ---------------
import Hazel.Tasks.messageRepeater as messageRepeater
# ---------------------
logger = logging.getLogger("Hazel.setup")

async def main(install_packages: bool=True):
    os.system('cls' if os.name == 'nt' else 'clear') # clear terminal
    print(art.text2art("HazelUB"))
    print(f"HazelUB is now booting...\n* If this is the first boot required packages may install.\nVersion: {Hazel.__version__}")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        config = load_config()
        db = DBClient(config[4])
        Hazel.SQLClient = db
        await db.init()
    except ImportError:
        logger.critical("python-dotenv not installed, Installing required packages...")
        install_status = install_requirements()
        if install_status == 0:
            logger.info("Packages installed successfully. Restarting setup...")
            return await main(install_packages=False)
        else:
            raise SystemExit(f"Setup Failed: Could not install required packages: {install_status}")

    is_installed = await db.is_installed()
    if not is_installed and install_packages:
        logger.info("Installing required packages...")
        install_status = install_requirements()
        if install_status == 0:
            logger.info("Packages installed successfully.")
        else:
            raise SystemExit(f"Setup Failed: Could not install required packages: {install_status}")
        await db.set_installed(True)
    logger.info("Starting telegram setup...")
    Tele = Telegram(config)
    Hazel.Tele = Tele # Override Tele in Hazel.__init__
    try:
        await Tele.create_pyrogram_clients()
        await Tele.start()
        os.system('cls' if os.name == 'nt' else 'clear') # clear terminal
        print(art.text2art("HazelUB"))
        print(f'Version: {Hazel.__version__}\nProcess ID: {os.getpid()}')
        logger.info("HazelUB is now running!")
        await asyncio.to_thread(startup_popup)
    except Exception as e:
        raise SystemExit(f"Setup Failed: {traceback.format_exc()}")
    
    # Tasks -----------------------
    logging.info('Starting HazelUB Tasks...')
    asyncio.create_task(messageRepeater.main(Tele, db))
    # -----------------------------
    
    for s in (SIGINT, SIGTERM, SIGABRT):
        signal_fn(s, signal_handler)
    while True:
        task = asyncio.create_task(asyncio.sleep(600))
        try:
            await task
        except asyncio.CancelledError:
            break