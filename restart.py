import os
import sys
import shutil

def restart():
    """Restart the HazelUB process in-place.

    Cleans up the ``Hazel/downloads`` directory (if it exists) and
    then replaces the current process with a fresh ``python -m Hazel``
    invocation via :func:`os.execv`, preserving any extra CLI arguments.
    """
    try:
        shutil.rmtree("Hazel/downloads")
    except: pass
    os.execv(
        sys.executable,
        [sys.executable, "-m", "Hazel"] + sys.argv[1:]
    )