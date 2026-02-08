from .utils import signal_handler, signal_handler, startup_popup, clear
from signal import signal as signal_fn, SIGINT, SIGTERM, SIGABRT
from .installation import main as installation_main
import traceback
import logging
import asyncio
import Hazel
import os

logger = logging.getLogger("Hazel.setup")

async def main(install_packages: bool=True):
    db, config = await installation_main()  # Ensure installation is done first.
    from MultiSessionManagement.telegram import Telegram
    from MultiSessionManagement.OneApi import main as oneApi_main
    import art
    
    logger.info("Starting telegram setup...")
    Tele = Telegram(config)
    Hazel.Tele = Tele # Override Tele in Hazel.__init__
    
    try:
        await Tele.create_pyrogram_clients()
        await Tele.start()

        clear()
        print(art.text2art("HazelUB"))
        print(
            f'Version: {Hazel.__version__}\n'
            f'Process ID: {os.getpid()}'
        )
        
        logger.info("HazelUB is now running!")
        await asyncio.to_thread(startup_popup)
    except Exception as e:
        raise SystemExit(f"Setup Failed: {traceback.format_exc()}")
    
    # Tasks -----------------------
    logging.info('Starting HazelUB Tasks...')

    import Hazel.Tasks.messageRepeater as messageRepeater

    asyncio.create_task(messageRepeater.main(Tele, db))
    # -- OneApi ---------------------------
    await oneApi_main(config[7], Hazel.Tele)
    # -- Idle System ---------------------------
    for s in (SIGINT, SIGTERM, SIGABRT): 
        signal_fn(s, signal_handler)
    while True:
        task = asyncio.create_task(asyncio.sleep(600))
        try:
            await task
        except asyncio.CancelledError:
            break
    # -----------------------------