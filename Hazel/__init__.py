import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from MultiSessionManagement.telegram import Telegram
    import Database.client as Database
    Tele: Telegram
    SQLClient: Database.DBClient

logging.basicConfig(
    format="[HazelUB] %(name)s: %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO
)

__version__ = "02.2026"
__channel__ = "DevsBase"
