import logging
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from MultiSessionManagement.telegram import Telegram
    import Database.client as Database
    Tele: Telegram
    SQLClient: Database.DBClient
else:
    Tele = None
    SQLClient = None

logging.Formatter.converter = lambda *args: time.gmtime(time.time() + 19800)

logging.basicConfig(
    format="[HazelUB] [%(asctime)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S %p",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO
)

__version__ = "02.2026 (OneApi)"
__channel__ = "DevsBase"
