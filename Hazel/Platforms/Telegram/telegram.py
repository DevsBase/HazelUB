import logging
from functools import partial
from typing import Dict, List, Optional, Set
from Setup.utils import HazelConfig

import pyrogram.filters as filters
from pyrogram.client import Client
from pyrogram.enums import ChatMemberStatus, MessageEntityType
from pyrogram.types import ChatMember, ChatPrivileges, Message, User
from pytgcalls import PyTgCalls

from .decorators import Decorators
from .download_song import DownloadSong
from .inline import InlineMethods
from .message import MessageMethods


class Telegram(
    DownloadSong,
    Decorators
):
    """Central orchestrator for multi-session Telegram userbot management.

    `Telegram` composes functionality from the :class:`Methods` and
    :class:`Decorators` mixins to provide a single entry-point for:

    * Creating and configuring multiple Pyrogram client sessions.
    * Managing the corresponding PyTgCalls (voice/video call) instances.
    * Starting / stopping all sessions in one call.
    * Looking up clients, privileges, and chat-member information.
    """

    def __init__(self, config: HazelConfig) -> None:
        """Initialise the Telegram manager from a configuration tuple.

        Unpacks connection credentials from *config*, initialises empty
        containers for clients, PyTgCalls instances, and privilege mappings,
        and overrides ``filters.command`` so that every command filter uses
        the custom command prefix(es) defined in the configuration.

        Args:
            config (HazelConfig): A tuple containing the necessary configuration values
        """
        # ----------- Config---------
        self.session: str = config.SESSION
        self.othersessions: List[str] = config.OtherSessions
        self.api_id: int = int(config.API_ID)
        self.api_hash: str = config.API_HASH
        self.bot_token: str = config.BOT_TOKEN
        # ----------- Clients ------------
        self.bot: Client = Client("HazelUB-Bot")
        self.mainClient: Client = Client("HazelUB")
        self.otherClients: List[Client] = []
        # ---------- Others -------------
        self._allClients: List[Client] = []
        self._allPyTgCalls: List[PyTgCalls] = []
        self._allClientsIds: Set[int] = set()
        self._clientPrivileges: Dict[Client, str] = {}
        self._clientPyTgCalls: Dict[Client, PyTgCalls] = {}

        filters.command = partial(filters.command, prefixes=config.PREFIX) # Override filters.command to set defualt prefixes
        # ---------- Methods -------------
        self.inline = InlineMethods
        self.message = MessageMethods

    async def create_pyrogram_clients(self) -> None:
        """Instantiate Pyrogram clients and PyTgCalls instances for every session.

        Builds all client objects in the following order:

        1. **Bot client** – if ``self.bot_token`` is longer than 50 characters
           it is treated as a session string; otherwise it is used as a plain
           bot token.
        2. **Main user client** – created from ``self.session``.
        3. **Additional user clients** – one per entry in ``self.othersessions``.

        Every user client is paired with a :class:`PyTgCalls` instance and
        assigned an initial privilege level:

        * The main client receives ``"sudo"`` privileges.
        * Additional clients receive ``"user"`` privileges (adjustable at
          runtime via the ``.cpromote`` / ``.cdemote`` commands).

        After this method returns, ``self._allClients`` and
        ``self._allPyTgCalls`` are fully populated and ready for
        :meth:`start`.
        """
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
        """Start the bot, all user clients, and their PyTgCalls instances.

        Startup sequence:

        1. The assistant bot (``self.bot``) is started first.
        2. Each user client in ``self._allClients`` is started in order;
           its associated :class:`PyTgCalls` instance (if any) is also
           started immediately after.
        3. Every user client silently attempts to join the HazelUB support
           channel (``Hazel.__channel__``); any failure is suppressed.
        """
        import Hazel
        __channel__ = Hazel.__channel__
        await self.bot.start()
        
        for client in self._allClients:
            await client.start()
            pytgcalls = self.getClientPyTgCalls(client)
            if pytgcalls:
                await pytgcalls.start()
            try:
                await client.join_chat(__channel__)
            except: ...
        
        self._allClientsIds: set[int] = {
            c.me.id for c in self._allClients if c.me
        }

        # it will delete the owner id if that client is not found in self._allClientsIds, and it will also remove the sudoers of that owner id.
        for x in list(Hazel.sudoers):
            if x not in self._allClientsIds:
                del Hazel.sudoers[x]

    async def stop(self) -> None:
        """Gracefully stop all user clients.

        Iterates over ``self._allClients`` and calls ``stop()`` on each
        Pyrogram client to disconnect from Telegram. The bot client is
        **not** stopped here.
        """
        for client in self._allClients:
            await client.stop()
    
    def getClientById(self, id: int | None = 0, m: Message | None = None) -> Optional[Client]:
        """Look up a user client by Telegram user ID.

        Resolution order:

        1. If *m* is a reply message, the sender ID of the replied-to message
           overrides *id*.
        2. ``self._allClients`` is searched for a client whose ``me.id``
           matches *id*.
        3. If no direct match is found, ``Hazel.sudoers`` is searched; if
           *id* belongs to a sudoer the **owner** client for that sudoer is
           returned instead.

        Args:
            id (int | None, optional): The Telegram user ID to search for.
                Defaults to ``0``.
            m (Message | None, optional): If provided and the message is a
                reply, the sender ID of the replied-to message is used as
                *id*. Defaults to ``None``.

        Returns:
            Optional[Client]: The matching :class:`Client` instance, or
            ``None`` if no client could be resolved.
        """
        import Hazel
        sudoers = Hazel.sudoers

        if m and isinstance(m, Message):
            if m.reply_to_message and hasattr(m.reply_to_message.from_user, 'id'):
                id = m.reply_to_message.from_user.id # type: ignore

        for client in self._allClients:
            if isinstance(id, int) and client.me and client.me.id == id: # type: ignore
                return client
            
        for _owner, _sudoers in list(Hazel.sudoers.items()):
            for _c in self._allClientsIds:
                if _c == _owner:
                    for _sudoer in _sudoers:
                        if id == _sudoer:
                            return self.getClientById(_owner)
        return
    
    
    def getClientPrivilege(self, client: Client | None = None, user_id: int | None = None) -> str | None:
        """Return the privilege level assigned to a client.

        At least one of *client* or *user_id* must be provided. If only
        *user_id* is given, :meth:`getClientById` is used to resolve the
        corresponding client first.

        Args:
            client (Client | None, optional): The Pyrogram client to query.
                Defaults to ``None``.
            user_id (int | None, optional): A Telegram user ID. Used to
                resolve the client when *client* is not provided.
                Defaults to ``None``.

        Returns:
            str | None: ``"sudo"`` for the primary (or promoted) client,
            ``"user"`` for all others. Returns ``None`` if the client
            cannot be resolved from *user_id*.

        Raises:
            ValueError: If both *client* and *user_id* are ``None`` / falsy.
        """
        if not user_id and not client:
            raise ValueError("client or user_id is required.")
        if not client and user_id:
            _client = self.getClientById(user_id)
            if _client: client = _client
        if client:
            return self._clientPrivileges.get(client, "user")
    
    def getClientPyTgCalls(self, client: Client) -> Optional[PyTgCalls]:
        """Return the :class:`PyTgCalls` instance associated with a client.

        If *client* is the bot account (``client.me.is_bot`` is ``True``),
        the method resolves it to the corresponding user client via
        :meth:`getClientById` before performing the lookup.

        Args:
            client (Client): The Pyrogram client whose associated
                :class:`PyTgCalls` instance is requested.

        Returns:
            Optional[PyTgCalls]: The matching :class:`PyTgCalls` instance,
            or ``None`` if no call handler is registered for the client.
        """
        if client.me and client.me.is_bot:
            id = client.me.id
            _client = self.getClientById(id)
            if _client: client = _client
        return self._clientPyTgCalls.get(client, None)
    
    async def is_admin(self, client: Client, chat_id: int, user_id: Optional[int] = None) -> bool:
        """Check whether a user is an admin or owner of a chat.

        If *user_id* is omitted the check is performed for the *client*'s
        own account.  On any API error the method logs the exception and
        returns `False` rather than propagating.

        Args:
            client (Client): The Pyrogram client to use for the API call.
            chat_id (int): The target chat / group / channel ID.
            user_id (Optional[int], optional): The user to check. Defaults
                to the *client*'s own user ID.

        Returns:
            bool: `True` if the user holds `ADMINISTRATOR` or `OWNER`
            status, `False` otherwise (including on errors).
        """
        try:
            if not user_id:
                user_id = client.me.id # type: ignore
            member = await client.get_chat_member(chat_id, user_id)
            return member.status in (
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER,
            )
        except Exception as e:
            logger = logging.getLogger("Hazel.Telegram.is_admin")
            logger.error(f"Error checking admin status: {str(e)}")
            return False
    
    async def get_chat_member_privileges(self, client: Client, chat_id: int, user_id: Optional[int] = None) -> Optional[ChatPrivileges]:
        """Retrieve the granular admin privileges of a user in a chat.

        If *user_id* is omitted the privileges are fetched for the
        *client*'s own account.  Returns `None` on any API error
        (logged at `ERROR` level).

        Args:
            client (Client): The Pyrogram client to use for the API call.
            chat_id (int): The target chat / group / channel ID.
            user_id (Optional[int], optional): The user whose privileges
                are requested. Defaults to the *client*'s own user ID.

        Returns:
            Optional[ChatPrivileges]: A :class:`ChatPrivileges` object
            describing the user's admin permissions, or `None` if the
            lookup fails.
        """
        try:
            if not user_id:
                user_id = client.me.id # type: ignore
            member = await client.get_chat_member(chat_id, user_id)
            return member.privileges
        except Exception as e:
            logger = logging.getLogger("Telegram.get_chat_member_privileges")
            logger.error(f"Error getting chat member privileges: {str(e)}")
            return None
    
    async def get_user(self, client: Client, message: Message | None = None, user_id: int | None = None, chat_id: Optional[int] = None, chat_member: bool = False) -> ChatMember | User | None | List[User]:
        """update soon
        """
        user = None
        if not chat_id and chat_member:
            raise ValueError("chat_id is required. when chat_member is True")
        elif not message and not user_id:
            raise ValueError("message or user_id is required.")
        elif user_id:
            user = user_id
        
        if message and message.reply_to_message and message.reply_to_message.from_user:
            user = message.reply_to_message.from_user.id
        elif message and message.entities and any(e.type == MessageEntityType.TEXT_MENTION for e in message.entities):
            for entity in message.entities: 
                if entity.type != MessageEntityType.TEXT_MENTION:
                    continue
                user = entity.user.id
                break
        elif message and message.text and message.command:
            if len(message.command) > 1:
                user = message.command[1].replace('@', '')
        
        if isinstance(user, str) and user.isdigit():
            user = int(user)
        if chat_member:
            if chat_id and user:
                return await client.get_chat_member(chat_id, user_id=user)
        elif user:
            return await client.get_users(user)