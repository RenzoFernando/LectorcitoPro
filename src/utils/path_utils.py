import os
import sys


def resource_path(relative_path: str) -> str:
    """
    Resolve the correct path to packaged resources both in development and when
    running from a PyInstaller binary.
    """
    try:
        base_path = sys._MEIPASS  # type: ignore
    except AttributeError:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, "recursos", relative_path)
