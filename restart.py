import os
import sys

def restart():
    try:
        os.remove("Hazel/downloads")
    except: pass
    os.execv(
        sys.executable,
        [sys.executable, "-m", "Hazel"] + sys.argv[1:]
    )