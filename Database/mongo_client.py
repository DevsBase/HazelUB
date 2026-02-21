from motor.motor_asyncio import AsyncIOMotorClient
from .Methods.repeatMethods import RepeatMethods
from .Methods.sessionMethods import SessionMethods

class MongoClient(RepeatMethods, SessionMethods):
    def __init__(self, mongo_url: str):
        self._client = AsyncIOMotorClient(mongo_url)
        self.db = self._client["UBdrag"]
        
        # Collections
        self.repeat_messages = self.db["repeat_messages"]
        self.repeat_groups = self.db["repeat_groups"]
        self.repeat_group_chats = self.db["repeat_group_chats"]
        self.local_state = self.db["local_state"]

    async def init(self):
        # Ensure local row exists in Mongo
        res = await self.local_state.find_one({"id": 1})
        if not res:
            await self.local_state.insert_one({"id": 1, "installed": False})

    async def is_installed(self) -> bool:
        row = await self.local_state.find_one({"id": 1})
        return row.get("installed", False) if row else False

    async def set_installed(self, value: bool):
        await self.local_state.update_one({"id": 1}, {"$set": {"installed": value}})
