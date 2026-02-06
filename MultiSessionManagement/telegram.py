from pyrogram.client import Client
from .decorators import Decorators
from pytgcalls import PyTgCalls
import pyrogram.filters as filters
from functools import partial
from typing import List

class Telegram(Decorators):
    def __init__(self, config: tuple) -> None:
        # ----------- Config---------
        self.session: str = config[3]
        self.othersessions: List[str] = config[5]
        self.api_id: int = int(config[1])
        self.api_hash: str = config[2]
        self.bot_token: str = config[0]
        # ----------- Clients ------------
        self.bot: Client | None = None
        self.mainClient: Client | None = None
        self.otherClients: List[Client] = []
        # ---------- Others -------------
        self._allClients: List[Client] = []
        self._allPyTgCalls: List[PyTgCalls] = []
        filters.command = partial(filters.command, prefixes=config[6]) # Override filters.command to set defualt prefixes
    
    async def create_pyrogram_clients(self) -> None:
        if len(self.bot_token) > 50: # Bot Client
            self.bot = Client(
                name="HazelUB-Bot",
                session_string=self.bot_token,
                api_hash=self.api_hash,
                api_id=self.api_id
             )
        else:
            self.bot = Client(
                name="HazelUB-Bot",
                bot_token=self.bot_token,
                api_hash=self.api_hash,
                api_id=self.api_id
             )
        # User Accounts ---------------------------------
        self.mainClient = Client( 
            name="HazelUB",
            session_string=self.session,
            api_id=self.api_id,
            api_hash=self.api_hash,
            plugins=dict(root="Mods/")
        )
        self.mainClient.privilege = "sudo" # type: ignore
        self.mainClient.pytgcalls: PyTgCalls = PyTgCalls(self.mainClient) # type: ignore

        for session in self.othersessions: # Other clients
            client = Client(
                name=f"HazelUB-{session:5}",
                session_string=session,
                api_id=self.api_id,
                api_hash=self.api_hash
            )
            client.privilege = "user" # type: ignore
            client.pytgcalls: PyTgCalls = PyTgCalls(client) # type: ignore
            self._allPyTgCalls.append(client.pytgcalls) # type: ignore
            self.otherClients.append(client)
        self._allClients = [self.mainClient, *self.otherClients]
        self._allPyTgCalls.append(self.mainClient.pytgcalls) # type: ignore

    async def start(self) -> None:
        # HazelUB v02.2026
        await self.bot.start() # type: ignore
        await self.mainClient.start() # type: ignore
        await self.mainClient.pytgcalls.start() # type: ignore
        for client in self.otherClients:
            await client.start()
            await client.pytgcalls.start() # type: ignore
        from Hazel import __channel__
        try:
            for client in self._allClients:
                await client.join_chat(__channel__)
        except: pass
    
    async def stop(self) -> None:
        for client in self._allClients:
            await client.stop()
    
    async def getClientById(self, id: int) -> Client | None:
        for client in self._allClients:
            if client.me and client.me.id == id: # type: ignore
                return client
        return None