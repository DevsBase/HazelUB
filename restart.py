import os
import sys
import shutil

def restart():
    try:
        shutil.rmtree("Hazel/downloads")
    except: pass
    os.execv(
        sys.executable,
        [sys.executable, "-m", "Hazel"] + sys.argv[1:]
    )