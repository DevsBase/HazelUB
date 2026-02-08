import logging
from OneApi.client import Client
from MultiSessionManagement.telegram import Telegram

logger = logging.getLogger(__name__)

async def main(
    url,
    Tele: Telegram,
    maxConnectionsForHazelClient: int=1
):
    oneClients = []
    for client in Tele._allClients:
        if client.is_connected and hasattr(client, "me") and client.me is not None:
            hazel_id = client.me.id
            oneClient = Client(url)
            await oneClient.connectHazelClient(hazel_id)
            oneClients.append(oneClient)
            if len(oneClients) >= maxConnectionsForHazelClient:
                break
    import Hazel
    Hazel.OneClients = oneClients # Override OneClients in Hazel.__init__
    