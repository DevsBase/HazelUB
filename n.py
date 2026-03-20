from neonize.client import NewClient
from neonize.events import ConnectedEv, MessageEv
from neonize.types import EventMessage

client = NewClient(name="hi")

# When connected
@client.event(ConnectedEv)
def on_connect(client, event):
    print("✅ Connected to WhatsApp")

# When message received
@client.event(MessageEv)
def on_message(client, event: MessageEv):
    msg: EventMessage = event.Message
    print("📩", msg)

client.connect()