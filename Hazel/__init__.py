from Essentials import *
from MultiSessionManagement.decorators import *

init = Init()
clients = CreateClients(init.get_config())
app, bot = clients.app, clients.bot
nexbot, DATABASE = clients.nexbot, clients.DATABASE