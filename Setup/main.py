from .utils import signal_handler, signal_handler, startup_popup, clear
from signal import signal as signal_fn, SIGINT, SIGTERM, SIGABRT
from .installation import main as installation_main
import traceback
import logging
import asyncio
import Hazel
import os

logger = logging.getLogger("Hazel.setup")

async def main():
    """Entry-point that orchestrates the full HazelUB startup lifecycle."""
    db, config = await installation_main()  # Ensure installation is done first.
    from Hazel.Platforms.Telegram import Telegram
    from Hazel.Platforms.Whatsapp import WhatsApp
    import art
    
    logger.info("Starting telegram setup...")
    Tele = Telegram(config)
    WA = WhatsApp()
    # override in Hazel.__init__
    Hazel.Tele = Tele 
    Hazel.WA = WA
    
    try:
        await Tele.create_pyrogram_clients()
        await Tele.start()
        WA.create_neonize_client("idk")

        clear()
        print(art.text2art("HazelUB"))
        print(
            f'Version: {Hazel.__version__}\n'
            f'Process ID: {os.getpid()}'
        )
        logger.info("Loading Mods...")
        from Hazel.ModLoader import load_mods; load_mods()
        
        logger.info("HazelUB is now running!")
        asyncio.create_task(asyncio.to_thread(startup_popup))
    except Exception as e:
        raise SystemExit(f"Setup Failed: {traceback.format_exc()}")
    
    # Tasks -----------------------
    logger.info('Starting HazelUB Tasks...')

    import Hazel.Platforms.Telegram.Tasks.messageRepeater as messageRepeater

    asyncio.create_task(messageRepeater.main(Tele, db))
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