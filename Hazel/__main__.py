from Hazel import *
import asyncio
from MultiSessionManagement import start_all
from clear import clear
import logging
import art

caption = f"""
![➡️](tg://emoji?id=6301092489273018328) **Hazel started** ![✅](tg://emoji?id=5260463209562776385)

![📱](tg://emoji?id=5346181118884331907) **Github:** [here](https://github.com/Otazuki004/HazelUB)
![☄️](tg://emoji?id=5361740325108857088) **Version:** ?
![❓](tg://emoji?id=5364286334477283372) **Support:** {Support}  
![⚠️](tg://emoji?id=5364241851500997604) **Channel:** {Channel}
"""

if __name__ == "__main__":
  a,b,c=clear(),print(art.text2art("HazelUB"), end=""),logging.info("Connecting...")
  asyncio.get_event_loop().run_until_complete(start_all())