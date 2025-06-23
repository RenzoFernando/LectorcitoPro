import sys
import os

# Obtiene la ruta correcta a los recursos, tanto en desarrollo como en el ejecutable de PyInstaller.
def resource_path(relative_path: str) -> str:
    try:
        # Si se ejecuta desde el empaquetado de PyInstaller, _MEIPASS contendrá la ruta al directorio temporal.
        base_path = sys._MEIPASS
    except AttributeError:
        # Si se ejecuta como un script normal, calcula la ruta base relativa al archivo actual.
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, 'recursos', relative_path)
