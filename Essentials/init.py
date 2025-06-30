import logging
import json
import os
import ast
from art import *
from clear import clear

log = logging.getLogger(__name__)

credits = """Cretor: Otazuki
Github: https://github.com/DevsBase/HazelUB
"""

class Init:
  def __init__(self):
    clear()
    print(text2art("HazelUB"), end="")
    print(credits)

    DefaultKeys = ['API_ID', 'API_HASH', 'PYROGRAM_SESSION', 'BOT_TOKEN', 'MONGO_DB_URL']
    OtherKeys = ['quick_start', 'OtherSessions']

    config = self._load_config_file()
    data = self._collect_config(DefaultKeys, config)
    self._process_other_keys(data, config, OtherKeys)
    self._confirm_data(DefaultKeys, data, config)

    self.__data = {
      "API_ID": int(data['API_ID']),
      "API_HASH": data['API_HASH'],
      "PYROGRAM_SESSION": data['PYROGRAM_SESSION'],
      "BOT_TOKEN": data['BOT_TOKEN'],
      "MONGO_DB_URL": data['MONGO_DB_URL'],
      "OtherSessions": data.get('OtherSessions', [])
    }

    if len(self.__data['OtherSessions']) > 7:
      raise ValueError("You cannot add more than 7 sessions.")

  def _load_config_file(self):
    try:
      if os.path.exists("config.json"):
        with open("config.json") as f:
          return json.load(f)
    except Exception as e:
      log.error(f"Failed to load config.json: {e}")
    return {}

  def _collect_config(self, DefaultKeys, config):
    data = {}
    warned = False

    for key in DefaultKeys:
      value = config.get(key) or os.getenv(key)
      if value is None:
        if not warned:
          log.info("Some of the keys are missing in config.json & ENV. You might promted to enter them manually.")
          warned = True
        try:
          while True:
            value = input(f"Enter your {key}: ")
            if value:
              break
        except EOFError:
          raise Exception("EOFError Occured. Please add your credentials in config.json or as a ENV.")
      data[key] = value
    return data

  def _process_other_keys(self, data, config, OtherKeys):
    for key in OtherKeys:
      if key == "OtherSessions":
        sessions = config.get(key) or os.getenv(key) or "[]"
        try: data[key] = ast.literal_eval(sessions)
        except Exception as e:
          data[key] = []
          if sessions and sessions != "[]": log.error(f"'OtherSessions' is variable found in config.json or in ENV. there is an error while converting it into List/Array: {e}.")    
        if not isinstance(data[key], list): data[key] = []
      else:
        data[key] = config.get(key) or os.getenv(key)

  def _confirm_data(self, DefaultKeys, data, config):
    try:
      if not config.get("quick_start"):
        print("Please check values below:")
        for key in DefaultKeys:
          print(f"{key}: {repr(data[key])}")
        confirm = input("Are these correct? (y/N): ").strip().lower()
      else: confirm = 'y'
    except EOFError:
      log.info("EOF detected. Continuing with y.")
      confirm = 'y'
    if confirm != 'y':
      Init()

  def save_config(self):
    if not hasattr(self, '_Init__data'):
      raise Exception("it seems like Init process isn't completed: cannot find Init.__data var.")
    try: config = self._load_config_file()
    except: config = None
    with open('config-backup.json', 'w') as f:
      if config: f.write(json.dumps(config, indent=2))
    with open('config.json', 'w') as f:
      json.dump({**self.__data, "quick_start": True}, f, indent=2)
    log.info("Configs are saved on config.json. also old config.json shifted to -> config-backup.json")
  def get_config(self):
    return self.__data.copy()