import logging
from MultiSessionManagement.telegram import Telegram
import Database.client as Database
from typing import TYPE_CHECKING

logging.basicConfig(
    format="[HazelUB] %(name)s: %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO
)

if TYPE_CHECKING:
    Tele: Telegram
    SQLClient: Database.DBClient
else:
    Tele = None
    SQLClient = None

__version__ = "01.2026"
__channel__ = "DevsBase"
