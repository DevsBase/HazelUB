from Essentials import *
from MultiSessionManagement.decorators import *
from .database import Database
import asyncio

pending: dict[str, asyncio.Future] = {}
config = Init()
clients = CreateClients(config)
app, bot = clients.app, clients.bot
db = Database(config.DB_URL)
llm, agent = create_agent(config)