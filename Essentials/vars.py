import logging
from datetime import datetime

start_time = datetime.now()
logging.basicConfig(format="[HazelUB] %(name)s: %(message)s",handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],level=logging.INFO)
HANDLER = [".","~","$","^","X"]
AutoJoinChats = ["FutureCity005", "DevsBase"]
Support = "FutureCity005"
Channel = "DevsBase"
__version__ = "0.0.1"