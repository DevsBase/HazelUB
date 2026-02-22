from typing import TYPE_CHECKING
from pyrogram import filters
from Hazel import sudoers

if TYPE_CHECKING:
    from MultiSessionManagement.telegram import Telegram
else:
    Telegram = None

class Decorators:
    def on_message(self: Telegram, filters_param: filters.Filter, sudo: bool = False, me: bool = True, group: int = 0): # type: ignore
        def decorator(func):
            if sudo:
                _filters = filters_param & filters.user(['self'] + sudoers)
                for i in self._allClients: 
                    i.on_message(filters=_filters, group=group)(func)
                return func
            else:
                if me: _filters = filters_param & filters.me
                else: _filters = filters_param
                
                for i in self._allClients: 
                    i.on_message(_filters, group=group)(func)
                return func
            
        return decorator
    
    def on_update(self: Telegram, *args): # type: ignore
        def decorator(func):
            for i in self._allPyTgCalls: 
                i.on_update(*args)(func)
            return func
        return decorator  