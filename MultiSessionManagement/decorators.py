from typing import TYPE_CHECKING
from pyrogram import filters
from Hazel import sudoers

if TYPE_CHECKING:
    from MultiSessionManagement.telegram import Telegram
    from pyrogram.types import Message
else:
    Telegram = None

class Decorators:
    def on_message(self: Telegram, filters_param: filters.Filter, sudo: bool = False, me: bool = True, group: int = 0): # type: ignore
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
        def decorator(func):
            for i in self._allPyTgCalls: 
                i.on_update(*args)(func)
            return func
        return decorator  