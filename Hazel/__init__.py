import logging
import time
from typing import TYPE_CHECKING, Dict, List

#import ensurepip

#3ensurepip.bootstrap()"""

if TYPE_CHECKING:
    import Database.client as Database
    from Hazel.Platforms.Telegram import Telegram
    Tele: Telegram
    SQLClient: Database.DBClient
    sudoers: Dict[int, List[int]]
    start_time: float
else:
    Tele = None
    SQLClient = None
    sudoers = {}
    start_time = time.time()
    
logging.Formatter.converter = lambda *args: time.gmtime(time.time() + 19800)

logging.basicConfig(
    format="[HazelUB] [%(asctime)s] %(name)s: %(message)s",
    datefmt="%I:%M %p | %d-%m",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO
)

__version__ = "03.2026"
__channel__ = "DevsBase"
__channel__ = "DevsBase"