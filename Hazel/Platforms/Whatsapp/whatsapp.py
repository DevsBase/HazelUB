from neonize.aioze.client import NewAClient
from neonize.aioze.events import MessageEv
from neonize.utils.jid import jid_is_lid
from typing import List, Callable, TypedDict, Dict
import logging
import traceback
import asyncio

logger = logging.getLogger("Platforms.WhatsApp")

class HandlersDict(TypedDict):
    command: str
    prefixes: List[str]
    from_me_only: bool
    from_users: List[str]

class WhatsApp:
    def __init__(self) -> None:
        self._allClients: List[NewAClient] = []
        self._handlers: Dict[Callable, HandlersDict] = {}
        self._semaphore = asyncio.Semaphore(50)
    
    def create_neonize_client(self, name: str, *args, **kwargs) -> NewAClient:
        client = NewAClient(name, *args, **kwargs)
        self._allClients.append(client)
        client.event(MessageEv)(self.update_handler)
        return client

    async def connect_neonize_client(self, client: NewAClient):
        if not isinstance(client, NewAClient):
            raise ValueError("Arg. client must be neonize.client.NewAClient")
        if client not in self._allClients:
            raise ValueError("Client is must be create with `create_neonize_client` method.")
        
        await client.connect()
    
    async def stop(self):
        for client in self._allClients:
            try:
                await client.stop()
            except:
                pass
    
    async def _safe_call(self, func: Callable, client: NewAClient, event: MessageEv):
        async with self._semaphore:
            try:
                await func(client, event)
            except Exception:
                logging.getLogger(func.__name__).exception(traceback.format_exc())
    
    async def update_handler(self, client: NewAClient, event: MessageEv):
        text = event.Message.conversation
        if isinstance(text, str):
            text = text.lower()
        else:
            logging.getLogger("Platforms.Whatsapp.update_handler").info(f"Message.conversation is not text. {text}")
            return
        
        sender = event.Info.MessageSource.Sender

        if jid_is_lid(sender):
            sender_alt = event.Info.MessageSource.SenderAlt
            sender = sender_alt if sender_alt.User else sender
            phone_number = sender.User
        else:
            phone_number = sender.User

        for func, meta in self._handlers.items():
            command = meta["command"]
            prefixes = meta["prefixes"]
            from_me_only = meta["from_me_only"]
            from_users = meta["from_users"]

            if from_me_only:
                if not event.Info.MessageSource.IsFromMe:
                    continue

            if from_users:
                user_matched = False
                if "me" in from_users:
                    if event.Info.MessageSource.IsFromMe:
                        user_matched = True
                
                if not user_matched and phone_number in from_users:
                    user_matched = True

                if not user_matched:
                    continue
            
            if prefixes:
                matched = False
                for prefix in prefixes:
                    if text.startswith(prefix + command):
                        matched = True
                        break
                if not matched:
                    continue
            else:
                if text != command:
                    continue
            
            asyncio.create_task(self._safe_call(func, client, event))

    def on_message(self, command: str, prefixes: List[str] = [], from_me_only: bool = False, from_users: List[str] = []):
        prefixes = prefixes or [".", "/"]
        from_users = from_users or []

        def decorator(func: Callable):
            normalized_users = [u.replace('+', '') for u in from_users]
            self._handlers[func] = {
                "command": command.lower(),
                "prefixes": prefixes,
                "from_me_only": from_me_only,
                "from_users": normalized_users
            }
            return func
        return decorator