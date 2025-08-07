import logging
import json
import os
import ast
from art import *
from clear import clear
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)

credits_text = """Cretor: Otazuki
Github: https://github.com/DevsBase/HazelUB
"""

required_keys = [
  'API_ID', 'API_HASH',
  'PYROGRAM_SESSION', 'BOT_TOKEN',
  'MONGO_DB_URL'
]

optional_keys = [
  'GOOGLE_API_KEY', 'OtherSessions'
]

class Init:
  def __init__(self):
    clear()
    print(text2art("HazelUB"), end="")
    print(credits_text)
    
    with open('config.json', 'r') as f:
      config = json.loads(f.read())
    
    for k in required_keys:
      v = config.get(k) or os.getenv(k)
      if not v:
        raise ValueError(f"{k} is not found in config.json or .env. {k} is an required key you must give it.")
      setattr(self, k, v)
      
    for k in optional_keys:
      v = config.get(k) or os.getenv(k)
      if v and k == "OtherSessions":
        v = ast.literal_eval(v)
      setattr(self, k, v)