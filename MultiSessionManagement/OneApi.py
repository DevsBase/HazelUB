import logging
import asyncio
from OneApi.client import Client
from MultiSessionManagement.telegram import Telegram
from MultiSessionManagement.decorators import OneApiDecorators

logger = logging.getLogger(__name__)

class OneApi(OneApiDecorators):
    def __init__(self, url, Tele: Telegram, maxConnectionsForHazelClient: int = 1) -> None:
        self.url = url
        self.Tele = Tele
        self.maxConnectionsForHazelClient = maxConnectionsForHazelClient
        self.HazelClients: list[Client] = []
    
    async def init(self):
        for client in self.Tele._allClients:
            if client.is_connected and hasattr(client, "me") and client.me is not None:
                hazel_id = client.me.id
                oneClient = Client(self.url)
                asyncio.create_task(oneClient.connectHazelClient(hazel_id))
                self.HazelClients.append(oneClient)
                if len(self.HazelClients) >= self.maxConnectionsForHazelClient:
                    break
        import Hazel
        Hazel.OneApi = self # Override HazelClients in Hazel.__init__
    
    async def getHazelClientById(self, id: int) -> Client | None:
        for client in self.HazelClients:
            if client.hazel_id == id:
                return client
        return None