class Decorators:
    def on_message(self, filters=None, group=0):
        def decorator(func):
            for i in self._allClients: # type: ignore
                i.on_message(filters, group=group)(func)
            return func
        return decorator
    
    def on_update(self, *args): # For PyTgCalls
        def decorator(func):
            for i in self.self._allPyTgCalls: # type: ignore
                i.on_update(*args)(func)
            return func
        return decorator  