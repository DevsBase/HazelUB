import logging
import time
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from MultiSessionManagement.telegram import Telegram
    from Database.mongo_client import MongoClient
    from Database.redis_client import RedisClient
    Tele: Telegram
    SQLClient: MongoClient
    Redis: RedisClient
else:
    Tele = None
    SQLClient = None
    Redis = None
    
logging.Formatter.converter = lambda *args: time.gmtime(time.time() + 19800)

logging.basicConfig(
    format="[HazelUB] [%(asctime)s] %(name)s: %(message)s",
    datefmt="%I:%M %p | %d-%m",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO
)

__version__ = "02.2026"
__channel__ = "DevsBase"
