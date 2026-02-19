from pyrogram.client import Client
from .decorators import Decorators
from pytgcalls import PyTgCalls
import pyrogram.filters as filters
from pyrogram.types import Message, ChatPrivileges
from functools import partial
from typing import List, Dict, Optional, Protocol
from pyrogram.enums import ChatMemberStatus
from .TelegramMethods import Methods
import logging

class Telegram(Methods, Decorators):
    def __init__(self, config: tuple) -> None:
        # ----------- Config---------
        self.session: str = config[3]
        self.othersessions: List[str] = config[5]
        self.api_id: int = int(config[1])
        self.api_hash: str = config[2]
        self.bot_token: str = config[0]
        # ----------- Clients ------------
        self.bot: Client = Client("HazelUB-Bot")
        self.mainClient: Client = Client("HazelUB")
        self.otherClients: List[Client] = []
        # ---------- Others -------------
        self._allClients: List[Client] = []
        self._allPyTgCalls: List[PyTgCalls] = []
        self._clientPrivileges: Dict[Client, str] = {}
        self._clientPyTgCalls: Dict[Client, PyTgCalls] = {}

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
            api_hash=self.api_hash
        )
        mainClientPyTgCalls = PyTgCalls(self.mainClient)
        self._clientPrivileges[self.mainClient] = "sudo"
        self._clientPyTgCalls[self.mainClient] = mainClientPyTgCalls

        for session in self.othersessions: # Other clients
            client = Client(
                name=f"HazelUB-{session:5}",
                session_string=session,
                api_id=self.api_id,
                api_hash=self.api_hash
            )
            clientPyTgCalls = PyTgCalls(client)
            
            self._clientPrivileges[client] = "user"
            self._clientPyTgCalls[client] = clientPyTgCalls

            self._allPyTgCalls.append(clientPyTgCalls)
            self.otherClients.append(client)
        
        self._allClients = [self.mainClient, *self.otherClients]
        self._allPyTgCalls.append(mainClientPyTgCalls)

    async def start(self) -> None:
        # HazelUB
        await self.bot.start()
        
        for client in self._allClients:
            await client.start()
            pytgcalls = self.getClientPyTgCalls(client)
            if pytgcalls:
                await pytgcalls.start()

        from Hazel import __channel__
        try:
            for client in self._allClients:
                await client.join_chat(__channel__)
        except:
            pass
    
    async def stop(self) -> None:
        for client in self._allClients:
            await client.stop()
    
    def getClientById(self, id: int | None = 0, m: Message | None = None) -> Optional[Client]:
        if m and isinstance(m, Message):
            if m.reply_to_message and hasattr(m.reply_to_message.from_user, 'id'):
                id = m.reply_to_message.from_user.id
        for client in self._allClients:
            if isinstance(id, int) and client.me and client.me.id == id: # type: ignore
                return client
        return None
    
    def getClientPrivilege(self, client: Client) -> str:
        return self._clientPrivileges.get(client, "user")
    
    def getClientPyTgCalls(self, client: Client) -> Optional[PyTgCalls]:
        return self._clientPyTgCalls.get(client, None)
    
    async def is_admin(self, client: Client, chat_id: int, user_id: Optional[int] = None) -> bool:
        try:
            if not user_id:
                user_id = client.me.id # type: ignore
            member = await client.get_chat_member(chat_id, user_id)
            return member.status in (
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER,
            )
        except Exception as e:
            logger = logging.getLogger("Telegram.is_admin")
            logger.error(f"Error checking admin status: {str(e)}")
            return False
    
    async def get_chat_member_privileges(self, client: Client, chat_id: int, user_id: Optional[int] = None) -> Optional[ChatPrivileges]:
        try:
            if not user_id:
                user_id = client.me.id # type: ignore
            member = await client.get_chat_member(chat_id, user_id)
            return member.privileges
        except Exception as e:
            logger = logging.getLogger("Telegram.get_chat_member_privileges")
            logger.error(f"Error getting chat member privileges: {str(e)}")
            return None