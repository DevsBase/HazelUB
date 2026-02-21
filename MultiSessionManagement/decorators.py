from typing import TYPE_CHECKING, List, Tuple, Any

if TYPE_CHECKING:
    from MultiSessionManagement.telegram import Telegram
else:
    Telegram = None

class Decorators:
    # Storage for dynamic registration
    _message_handlers: List[Tuple[Any, int, Any]] = [] # (filters, group, func)
    _update_handlers: List[Tuple[Any, Any]] = [] # (args, func)

    def on_message(self: Telegram, filters=None, group=0): # type: ignore
        def decorator(func):
            # Store for later
            self._message_handlers.append((filters, group, func))
            
            # Register to current clients
            for i in self._allClients: 
                i.on_message(filters, group=group)(func)
            return func
        return decorator
    
    def on_update(self: Telegram, *args): # type: ignore
        def decorator(func):
            # Store for later
            self._update_handlers.append((args, func))
            
            # Register to current clients
            for i in self._allPyTgCalls: 
                i.on_update(*args)(func)
            return func
        return decorator  