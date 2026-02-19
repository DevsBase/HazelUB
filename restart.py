import os
import sys

def restart():
    os.execv(
        sys.executable,
        [sys.executable, "-m", "Hazel"] + sys.argv[1:]
    )