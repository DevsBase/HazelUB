import os
import importlib
import traceback

def load_mods():
    mods_dir = os.path.dirname(__file__)
    mods_pkg = __name__

    print(f"[Mods] Loading from: {mods_dir}")
    print(f"[Mods] Package name: {mods_pkg}")

    for file in os.listdir(mods_dir):
        if file.endswith(".py") and not file.startswith("_"):
            module = f"{mods_pkg}.{file[:-3]}"
            try:
                importlib.import_module(module)
                print(f"[Mods] Loaded: {module}")
            except Exception as e:
                print(f"[Mods] FAILED: {module}")
                traceback.print_exc()
