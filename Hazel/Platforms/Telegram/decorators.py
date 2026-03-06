from typing import TYPE_CHECKING

import pyrogram
from cachetools import TTLCache
from pyrogram import filters
from pyrogram.types import Message, InlineQuery

from Hazel import sudoers

if TYPE_CHECKING:
    from Hazel.Platforms.Telegram import Telegram
else:
    Telegram = None


BC_OWNER_CACHE: TTLCache[str, int] = TTLCache(maxsize=1000, ttl=600)


async def sudo_check(_, client: pyrogram.client.Client, message: Message | InlineQuery) -> bool:
    """Check if the user is sudo."""
    import Hazel

    if not message.from_user or not client.me:
        return False

    if message.from_user.is_self and not client.me.is_bot:
        return True

    user_id: int = message.from_user.id

    if user_id in sudoers.get(client.me.id, []):
        return True

    if isinstance(message, Message) and message.business_connection_id:
        for _sudoers in Hazel.sudoers.values():
            if user_id in _sudoers:
                if BC_OWNER_CACHE.get(message.business_connection_id) == user_id:
                    return True
                else:
                    bc_conn = await client.get_business_connection(
                        message.business_connection_id
                    )
                    if bc_conn and bc_conn.user.id == user_id:
                        BC_OWNER_CACHE[message.business_connection_id] = user_id
                        return True

    if isinstance(message, Message) and not message.business_connection_id and client.me.is_bot:
        # If it's a bot client and the message is not from a business connection, check if the user is a sudoer for any of the owner's clients
        for _sudoers in Hazel.sudoers.values():
            if user_id in _sudoers:
                return True

    if not hasattr(message, 'business_connection_id'):
        if user_id in Hazel.Tele._allClientsIds:
            return True
    return False


class Decorators:
    """Mixin class providing decorator methods for registering message and call handlers.

    This class is designed to be used as a mixin with the ``Telegram`` class. It
    provides convenience decorators that automatically register handler functions
    across **all** active Pyrogram client sessions and PyTgCalls instances, enabling
    multi-session support with a single decorator call.
    """

    def on_message(self: Telegram, filters_param: filters.Filter, sudo: bool = False, business_bot: bool = True, inline: bool = False, group: int = 0):  # type: ignore
        """
            update soon
        """

        def decorator(func):
            for i in self._allClients:
                if sudo:
                    _filters = filters_param & filters.create(sudo_check)
                else:
                    _filters = filters_param

                i.on_message(_filters, group=group)(func)

            if sudo and business_bot:
                _bot_filters = filters_param & filters.create(sudo_check)
                self.bot.on_business_message(_bot_filters, group=group)(func)
            if sudo and inline:
                _inline_filters = filters_param & filters.create(sudo_check)
                self.bot.on_inline_query(_inline_filters)(func)
            return func

        return decorator

    def on_update(self: Telegram, *args):  # type: ignore
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
