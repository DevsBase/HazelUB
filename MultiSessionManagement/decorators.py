from MultiSessionManagement.telegram import Telegram
from MultiSessionManagement.OneApi import OneApi

class Decorators:
    def on_message(self: Telegram, filters=None, group=0): # type: ignore
        def decorator(func):
            for i in self._allClients: 
                i.on_message(filters, group=group)(func)
            return func
        return decorator
    
    def on_update(self: Telegram, *args): # type: ignore
        def decorator(func):
            for i in self._allPyTgCalls: 
                i.on_update(*args)(func)
            return func
        return decorator  

class OneApiDecorators:
    def on_hazel_client_update(self: OneApi): # type: ignore
        def decorator(func):
            for client in self.HazelClients: 
                client.registerHandler('hazelClient', func)
            return func
        return decorator