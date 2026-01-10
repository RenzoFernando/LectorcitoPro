
from __future__ import annotations

from tkinter import filedialog


def ask_directory(title: str = "", initial_dir: str | None = None) -> str:
    """Abre un selector de carpetas del sistema.

    Devuelve una ruta (str) o "" si el usuario cancela.
    """
    return filedialog.askdirectory(title=title, initialdir=initial_dir) or ""
