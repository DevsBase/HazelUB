from Essentials import *
from MultiSessionManagement.decorators import *

config = Init()
clients = CreateClients(config)
app, bot = clients.app, clients.bot

llm, agent = create_agent(config)