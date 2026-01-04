import os
import sys


def resource_path(relative_path: str) -> str:
    """
    Obtiene la ruta correcta a los recursos tanto en desarrollo como cuando se
    ejecuta desde un binario de PyInstaller.
    """
    try:
        base_path = sys._MEIPASS  # type: ignore
    except AttributeError:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, "recursos", relative_path)
