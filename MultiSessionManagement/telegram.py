from pyrogram.client import Client
from .decorators import Decorators
from pytgcalls import PyTgCalls
import pyrogram.filters as filters
from pyrogram.types import Message, ChatPrivileges, ChatMember, User
from functools import partial
from typing import List, Dict, Optional, Protocol
from pyrogram.enums import ChatMemberStatus, MessageEntityType
from .TelegramMethods import Methods
import logging

class Telegram(Methods, Decorators):
    """Central orchestrator for multi-session Telegram userbot management.

    ``Telegram`` composes functionality from the :class:`Methods` and
    :class:`Decorators` mixins to provide a single entry-point for:

    * Creating and configuring multiple Pyrogram client sessions.
    * Managing the corresponding PyTgCalls (voice/video call) instances.
    * Starting / stopping all sessions in one call.
    * Looking up clients, privileges, and chat-member information.

    Attributes:
        session (str): Session string for the primary user account.
        othersessions (List[str]): Session strings for additional user accounts.
        api_id (int): Telegram API application ID.
        api_hash (str): Telegram API application hash.
        bot_token (str): Bot token **or** session string for the assistant bot.
        bot (Client): Pyrogram client for the assistant bot.
        mainClient (Client): Pyrogram client for the primary user account.
        otherClients (List[Client]): Pyrogram clients for secondary accounts.
        _allClients (List[Client]): Convenience list of *all* user clients
            (``mainClient`` + ``otherClients``).
        _allPyTgCalls (List[PyTgCalls]): All PyTgCalls instances.
        _clientPrivileges (Dict[Client, str]): Maps each client to its
            privilege level (``"sudo"`` or ``"user"``).
        _clientPyTgCalls (Dict[Client, PyTgCalls]): Maps each client to its
            corresponding PyTgCalls instance.
    """

    def __init__(self, config: tuple) -> None:
        """Initialise the Telegram manager from a configuration tuple.

        Unpacks connection credentials from *config* and sets up empty
        containers for clients, PyTgCalls instances, and privilege mappings.
        Also overrides ``filters.command`` to use the custom command prefixes
        specified in the configuration.

        Args:
            config (tuple): A tuple with the following positional elements:

                * ``[0]`` – Bot token or bot session string.
                * ``[1]`` – Telegram API ID.
                * ``[2]`` – Telegram API hash.
                * ``[3]`` – Primary user session string.
                * ``[5]`` – List of additional user session strings.
                * ``[6]`` – Command prefix(es) (e.g. ``"."`` or ``["." , "!"]``).
        """
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
        """Instantiate Pyrogram clients and PyTgCalls instances for every session.

        Creates the assistant bot client (using either a session string or a
        plain bot token, depending on the length of ``self.bot_token``), the
        primary user client, and one additional client per entry in
        ``self.othersessions``.  Each user client is paired with a
        :class:`PyTgCalls` instance and assigned a privilege level:

        * The primary client receives ``"sudo"`` privileges.
        * Additional clients receive ``"user"`` privileges. (can be changed with `cpromote` command.)

        After this method completes, ``self._allClients`` and
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

        Startup order:

        1. The assistant bot (``self.bot``).
        2. Each user client in ``self._allClients``, followed by its
           associated PyTgCalls instance (if present).
        3. Every user client attempts to join the HazelUB support channel
           (silently ignored on failure).
        """
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
        """Gracefully stop all user clients.

        Iterates over ``self._allClients`` and calls ``stop()`` on each
        Pyrogram client to disconnect from Telegram.
        """
        for client in self._allClients:
            await client.stop()
    
    def getClientById(self, id: int | None = 0, m: Message | None = None) -> Optional[Client]:
        """Look up a user client by its Telegram user ID.

        If a :class:`Message` is provided and it is a reply, the user ID is
        automatically extracted from the replied-to message's sender, which
        is useful for commands like *".info"* that target the replied user.

        Args:
            id (int | None, optional): The Telegram user ID to search for.
                Defaults to ``0``.
            m (Message | None, optional): A Pyrogram message. If it is a
                reply, the sender ID of the replied message overrides *id*.
                Defaults to ``None``.

        Returns:
            Optional[Client]: The matching :class:`Client` instance, or
            ``None`` if no client with the given ID is found.
        """
        if m and isinstance(m, Message):
            if m.reply_to_message and hasattr(m.reply_to_message.from_user, 'id'):
                id = m.reply_to_message.from_user.id # type: ignore
        for client in self._allClients:
            if isinstance(id, int) and client.me and client.me.id == id: # type: ignore
                return client
        return None
    
    def getClientPrivilege(self, client: Client) -> str:
        """Return the privilege level of a client.

        Args:
            client (Client): The Pyrogram client to query.

        Returns:
            str: ``"sudo"`` for the primary account, ``"user"`` for all
            others. Unless you haven't changed the privilege by `.cpromote` or `.cdemote` command.
        """
        return self._clientPrivileges.get(client, "user")
    
    def getClientPyTgCalls(self, client: Client) -> Optional[PyTgCalls]:
        """Return the PyTgCalls instance associated with a client.

        Args:
            client (Client): The Pyrogram client whose call instance is
                requested.

        Returns:
            Optional[PyTgCalls]: The corresponding :class:`PyTgCalls`
            instance, or ``None`` if the client has no associated call
            handler.
        """
        return self._clientPyTgCalls.get(client, None)
    
    async def is_admin(self, client: Client, chat_id: int, user_id: Optional[int] = None) -> bool:
        """Check whether a user is an admin or owner of a chat.

        If *user_id* is omitted the check is performed for the *client*'s
        own account.  On any API error the method logs the exception and
        returns ``False`` rather than propagating.

        Args:
            client (Client): The Pyrogram client to use for the API call.
            chat_id (int): The target chat / group / channel ID.
            user_id (Optional[int], optional): The user to check. Defaults
                to the *client*'s own user ID.

        Returns:
            bool: ``True`` if the user holds ``ADMINISTRATOR`` or ``OWNER``
            status, ``False`` otherwise (including on errors).
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
            logger = logging.getLogger("Telegram.is_admin")
            logger.error(f"Error checking admin status: {str(e)}")
            return False
    
    async def get_chat_member_privileges(self, client: Client, chat_id: int, user_id: Optional[int] = None) -> Optional[ChatPrivileges]:
        """Retrieve the granular admin privileges of a user in a chat.

        If *user_id* is omitted the privileges are fetched for the
        *client*'s own account.  Returns ``None`` on any API error
        (logged at ``ERROR`` level).

        Args:
            client (Client): The Pyrogram client to use for the API call.
            chat_id (int): The target chat / group / channel ID.
            user_id (Optional[int], optional): The user whose privileges
                are requested. Defaults to the *client*'s own user ID.

        Returns:
            Optional[ChatPrivileges]: A :class:`ChatPrivileges` object
            describing the user's admin permissions, or ``None`` if the
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
    
    async def get_user(self, client: Client, message: Message, chat_id: Optional[int] = None, chat_member: bool = False) -> ChatMember | User | None | List[User]:
        """Resolve a target user from a message using multiple strategies.

        The method tries the following strategies **in order** to determine
        the target user:

        1. **Reply** – If the message is a reply, use the replied-to
           message's sender.
        2. **Text mention** – If the message contains a ``TEXT_MENTION``
           entity (a mention of a user without a public username), use that
           user's ID.
        3. **Text argument** – Otherwise, split the message text and treat
           the first argument after the command as a username or user ID
           (leading ``@`` is stripped).

        Args:
            client (Client): The Pyrogram client to use for API lookups.
            message (Message): The incoming message that triggered the
                command.
            chat_id (Optional[int], optional): Required when
                *chat_member* is ``True``. The chat in which to look up the
                user's membership.
            chat_member (bool, optional): If ``True``, return a
                :class:`ChatMember` object instead of a plain :class:`User`.
                Requires *chat_id* to be set. Defaults to ``False``.

        Returns:
            ChatMember | User | None | List[User]: The resolved user
            object, a :class:`ChatMember` (when *chat_member* is ``True``),
            or ``None`` if no user could be determined.

        Raises:
            ValueError: If *chat_member* is ``True`` but *chat_id* is not
                provided.
        """
        user = None
        if not chat_id and chat_member:
            raise ValueError("chat_id is required. when chat_member is True")
        if message.reply_to_message and message.reply_to_message.from_user:
            user = message.reply_to_message.from_user.id
        elif message.entities and any(e.type == MessageEntityType.TEXT_MENTION for e in message.entities):
            for entity in message.entities: 
                if entity.type != MessageEntityType.TEXT_MENTION:
                    continue
                user = entity.user.id
                break
        elif message.text:
            user = (message.text.split(None, 1)[1]).replace('@', '')
        
        if isinstance(user, str) and user.isdigit():
            try: user = int(user)
            except: return None
        
        if chat_member:
            if chat_id and user:
                return await client.get_chat_member(chat_id, user_id=user)
        if user:
            return await client.get_users(user)