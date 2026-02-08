import os
import importlib
import traceback
import logging

logger = logging.getLogger(__name__)

def load_mods():
    mods_dir = os.path.dirname(__file__)
    mods_pkg = __name__
    loaded = []

    for file in os.listdir(mods_dir):
        if file.endswith(".py") and not file.startswith("_"):
            module = f"{mods_pkg}.{file[:-3]}"
            try:
                importlib.import_module(module)
                loaded.append(module)
            except Exception as e:
                logger.error(f"[FAILED TO LOAD]: {module}")
                traceback.print_exc()
    logger.info(f"[Mods] Loaded: {', '.join(loaded)}")
