from Essentials import *
from MultiSessionManagement.decorators import *

config = Init()
clients = CreateClients(config)
app, bot = clients.app, clients.bot
nexbot, DATABASE = clients.nexbot, clients.DATABASE

llm, agent = create_agent(config)