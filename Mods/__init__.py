import os
import importlib

def load_mods():
    mods_dir = os.path.dirname(__file__)
    mods_pkg = __name__

    for file in os.listdir(mods_dir):
        if file.endswith(".py") and not file.startswith("_"):
            importlib.import_module(f"{mods_pkg}.{file[:-3]}")
