import logging
import time
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from MultiSessionManagement.telegram import Telegram
    import Database.client as Database
    Tele: Telegram
    SQLClient: Database.DBClient
    sudoers: List[int]
else:
    Tele = None
    SQLClient = None
    sudoers = {}
    
logging.Formatter.converter = lambda *args: time.gmtime(time.time() + 19800)

logging.basicConfig(
    format="[HazelUB] [%(asctime)s] %(name)s: %(message)s",
    datefmt="%I:%M %p | %d-%m",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO
)

__version__ = "02.2026"
__channel__ = "DevsBase"
