import os
import sys
from contextlib import contextmanager
from pathlib import Path
from time import perf_counter


def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        if sys._MEIPASS:
            base_path = "./_internal"  # sys._MEIPASS
        elif getattr(sys, "frozen", False):
            base_path = os.path.dirname(sys.executable)
    except Exception:
        base_path = "."  # os.path.abspath(".")

    return Path(base_path, "resources", relative_path)


@contextmanager
def timer() -> float:
    t1 = t2 = perf_counter()
    yield lambda: t2 - t1
    t2 = perf_counter()
