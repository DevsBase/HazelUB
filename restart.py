import os
import sys

def restart():
    os.execv(
        sys.executable,
        [sys.executable, "-B", "-m", "Hazel"] + sys.argv[1:]
    )