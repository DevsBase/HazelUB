from typing import TYPE_CHECKING, List, Tuple, Any
import logging
import pyrogram
from pyrogram import handlers, StopPropagation, ContinuePropagation
from pyrogram.types import Message

logger = logging.getLogger("Hazel.Decorators")

if TYPE_CHECKING:
    from MultiSessionManagement.telegram import Telegram
else:
    Telegram = None

class Decorators:
    def on_message(self: Telegram, filters=None, group=0, sudo=False, fsudo=False, allow_all=False): # type: ignore
        def decorator(func):
            # Internal auth wrapper
            async def auth_check(client, message: Message):
                try:
                    # Extract ID
                    uid = None
                    if message.from_user:
                        uid = message.from_user.id
                    elif message.sender_chat:
                        uid = message.sender_chat.id
                    
                    if uid is None:
                        return
                    
                    # 1. Allow all (public listeners)
                    if allow_all:
                        return await func(client, message)

                    # 2. Always allow the bot owner (me)
                    if uid == client.me.id:
                        return await func(client, message)
                    
                    from Hazel import SQLClient
                    if not SQLClient:
                        return

                    # 3. Check for FSudo (Full access)
                    is_fsudo_user = await SQLClient.is_fsudo(uid)
                    
                    if fsudo: # Only owner or FSudo
                        if is_fsudo_user:
                            return await func(client, message)
                        return
                    
                    # 4. Check for Sudo (Restricted access)
                    if sudo: # Owner or FSudo or Sudo
                        is_sudo_user = await SQLClient.is_sudo(uid)
                        if is_fsudo_user or is_sudo_user:
                            return await func(client, message)
                        return
                    
                    # Default: reject others
                    return
                # Do NOT catch propagation control exceptions
                except (StopPropagation, ContinuePropagation):
                    raise
                except Exception as e:
                    # Silent in production unless critical
                    pass

            if not hasattr(self, "_message_handlers"):
                self._message_handlers = []
            
            # Store for dynamic client loading
            self._message_handlers.append((filters, group, auth_check))
            
            clients = getattr(self, "_allClients", [])
            for client in clients:
                try:
                    client.add_handler(
                        handlers.MessageHandler(auth_check, filters),
                        group
                    )
                except Exception:
                    pass
            return auth_check
        return decorator
    
    def on_update(self: Telegram, *args): # type: ignore
        def decorator(func):
            if not hasattr(self, "_update_handlers"):
                self._update_handlers = []
                
            self._update_handlers.append((args, func))
            
            calls = getattr(self, "_allPyTgCalls", [])
            for pytgcalls in calls:
                try:
                    pytgcalls.on_update(*args)(func)
                except Exception:
                    pass
            return func
        return decorator  