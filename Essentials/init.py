import logging
import json
from art import *
from clear import clear
import ast
log = logging.getLogger(__name__)

credits = """Cretor: Otazuki
Github: https://github.com/DevsBase/HazelUB
"""

class Init:
  def __init__(self):
    import os
    clear()
    print(text2art("HazelUB"), end="")
    print(credits)
    DefaultKeys = ['API_ID', 'API_HASH', 'PYROGRAM_SESSION', 'BOT_TOKEN', 'MONGO_DB_URL']
    OtherKeys = ['quick_start', 'OtherSessions']
    data, config = {}, {}
    if os.path.exists("config.json"):
      try:
        with open("config.json") as f:
          config = json.load(f)
      except Exception as e:
        log.error(f"Failed to load config.json: {e}")
    warned = False
    for key in DefaultKeys:
      if not (config.get(key) or os.getenv(key)):
        if (not warned):
          log.info("Some of the keys are missing in config.json & ENV. You might promted to enter them manually.")
          warned = True
        try:
          while (True):
            i = input(f"Enter your {key}: ")
            if i: break
        except EOFError:
          raise Exception("EOFError Occured. Please add your credentials in config.json or as a ENV.")
        data[key] = config.get(key) or os.getenv(key) or i
      else: data[key] = config.get(key) or os.getenv(key)
    for k in OtherKeys:
      data[k] = config.get(k)
      if k == "OtherSessions":
        data[k] = config.get(k,[]) or eval((os.getenv(k) or "[]"))
        if not isinstance(data[k], list): data[k]=[]
    try:
      if not (config.get('quick_start')):
        print("Please check values below:")
        for key in DefaultKeys:
          print(f"{key}: {repr(data[key])}")
        confirm = input("Are these correct? (y/n): ").strip().lower()
      else: confirm = 'y'
    except EOFError:
      log.info("EOF detected. Continuing with y.")
      confirm = "y"
    if confirm != "y":
      for key in DefaultKeys:
        try:
          data[key] = input(f"Enter {key}: ").strip()
        except EOFError:
          log.error(f"EOF detected while entering {key}. Exiting.")
          exit()
    self.output = {
      "API_ID": int(data['API_ID']),
      "API_HASH": data['API_HASH'],
      "PYROGRAM_SESSION": data['PYROGRAM_SESSION'],
      "BOT_TOKEN": data['BOT_TOKEN'],
      "OtherSessions": data.get('OtherSessions')
    }
    if len(data.get('OtherSessions')) > 7:
      raise ValueError("You cannot add more than 7 sessions.")