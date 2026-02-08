import logging
import time
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from MultiSessionManagement.telegram import Telegram
    from OneApi.client import Client
    import Database.client as Database
    Tele: Telegram
    SQLClient: Database.DBClient
    OneClients: List[Client]
else:
    Tele = None
    SQLClient = None
    OneClients = []

logging.Formatter.converter = lambda *args: time.gmtime(time.time() + 19800)

logging.basicConfig(
    format="[HazelUB] [%(asctime)s] %(name)s: %(message)s",
    datefmt="%I:%M %p | %d/%m",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO
)

__version__ = "02.2026 (OneApi)"
__channel__ = "DevsBase"
