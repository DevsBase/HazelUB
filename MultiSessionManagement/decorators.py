from typing import TYPE_CHECKING
from pyrogram import filters
from Hazel import sudoers
from pyrogram.types import Message

if TYPE_CHECKING:
    from MultiSessionManagement.telegram import Telegram
else:
    Telegram = None

class Decorators:
    """Mixin class providing decorator methods for registering message and call handlers.

    This class is designed to be used as a mixin with the ``Telegram`` class. It
    provides convenience decorators that automatically register handler functions
    across **all** active Pyrogram client sessions and PyTgCalls instances, enabling
    multi-session support with a single decorator call.
    """

    def on_message(self: Telegram, filters_param: filters.Filter, sudo: bool = False, me: bool = True, group: int = 0): # type: ignore
        """Register a message handler across all Pyrogram client sessions.

        This decorator iterates over every client in ``self._allClients`` and
        registers the decorated function as a message handler on each one. It
        supports three access-control modes controlled by the ``sudo`` and
        ``me`` flags:

        * **sudo=True** – The handler is triggered for the account owner
          *and* any user whose ID is present in the per-client ``sudoers``
          dictionary (``Hazel.sudoers``).
        * **me=True** (default) – The handler is restricted to messages sent
          by the client's own account (``filters.me``).
        * **me=False, sudo=False** – No ownership filter is applied; the
          handler fires for *all* incoming messages that match
          ``filters_param``.

        Args:
            filters_param (filters.Filter): A Pyrogram filter (or combination
                of filters) that determines which messages trigger the handler.
                For example, ``filters.command("ping")``.
            sudo (bool, optional): If ``True``, allow both the account owner
                and authorised sudo users to trigger the handler. When enabled,
                the ``me`` flag is ignored. Defaults to ``False``.
            me (bool, optional): If ``True``, restrict the handler to messages
                sent by the client's own account. Ignored when ``sudo`` is
                ``True``. Defaults to ``True``.
            group (int, optional): The handler group number. Handlers in the
                same group are mutually exclusive; handlers in different groups
                are independent. Defaults to ``0``.

        Returns:
            Callable: A decorator that registers the wrapped function as a
            message handler on every active client session.

        Example::

            @app.on_message(filters.command("ping"))
            async def ping_handler(client, message):
                await message.reply("Pong!")

            @app.on_message(filters.command("ban"), sudo=True)
            async def ban_handler(client, message):
                # Both the owner and sudo users can trigger this.
                ...
        """
        def decorator(func):
            for i in self._allClients: 
                if sudo:
                    async def sudo_check(_, client, message: Message):
                        if not message.from_user: return False
                        if message.from_user.is_self: return True
                        return message.from_user.id in sudoers.get(client.me.id, [])
                        
                    _filters = filters_param & filters.create(sudo_check)
                else:
                    if me: _filters = filters_param & filters.me
                    else: _filters = filters_param
                
                i.on_message(_filters, group=group)(func)
            return func
            
        return decorator
    
    def on_update(self: Telegram, *args): # type: ignore
        """Register a PyTgCalls update handler across all call instances.

        This decorator iterates over every ``PyTgCalls`` instance in
        ``self._allPyTgCalls`` and registers the decorated function as an
        update handler on each one. This is primarily used to listen for
        voice/video call events such as stream end, participant changes, etc.

        Args:
            *args: Positional arguments forwarded directly to
                ``PyTgCalls.on_update()``. Typically this includes the update
                filter(s) specifying which call events to listen for.

        Returns:
            Callable: A decorator that registers the wrapped function as a
            call-update handler on every active PyTgCalls instance.

        Example::

            @app.on_update(filters.stream_end)
            async def on_stream_end(client, update):
                # Handle the end of an audio/video stream.
                ...
        """
        def decorator(func):
            for i in self._allPyTgCalls: 
                i.on_update(*args)(func)
            return func
        return decorator  