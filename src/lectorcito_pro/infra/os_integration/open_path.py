
import os
import webbrowser


def open_path(path: str) -> None:
    """Abre un archivo/carpeta con el sistema operativo."""
    webbrowser.open(os.path.realpath(path))
