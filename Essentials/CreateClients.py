from pyrogram import *
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import Nexgram

log = logging.getLogger(__name__)

class CreateClients:
  def __init__(self, config):
    API_ID, API_HASH = config.API_ID, config.API_HASH
    PYROGRAM_SESSION, BOT_TOKEN = config.PYROGRAM_SESSION, config.BOT_TOKEN
    MONGO_DB_URL = config.MONGO_DB_URL
    
    from .vars import __version__
    self.app = Client("UB", session_string=PYROGRAM_SESSION, api_id=API_ID, api_hash=API_HASH, device_model="HazelUB", system_version=f"HazelUB (v{__version__})", plugins=dict(root="Hazel/plugins"))
    
    if len(BOT_TOKEN) > 50: self.bot = Client("Bot", session_string=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)
    else: self.bot = Client("Bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)
    
    self.DATABASE = AsyncIOMotorClient(MONGO_DB_URL)["Something"]
    
    from MultiSessionManagement import add_client
    
    add_client(self.app)
    if config.OtherSessions:
      for i in config.OtherSessions:
        add_client(Client("otherClient", session_string=i, api_id=API_ID, api_hash=API_HASH, device_model="HazelUB", in_memory=True, system_version=f"HazelUB (v{__version__})"))