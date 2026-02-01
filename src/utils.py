import sys
import os
import logging
import traceback

# Importamos config para obtener la ruta del log
try:
    import config
except ImportError:
    # Fallback si se importa desde un contexto donde config no es visible (raro en este setup)
    config = None


# Obtiene la ruta correcta a los recursos, tanto en desarrollo como en el ejecutable de PyInstaller.
def resource_path(relative_path: str) -> str:
    try:
        # Si se ejecuta desde el empaquetado de PyInstaller, _MEIPASS contendrá la ruta al directorio temporal.
        base_path = sys._MEIPASS
    except AttributeError:
        # Si se ejecuta como un script normal, calcula la ruta base relativa al archivo actual.
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, 'recursos', relative_path)


# --- SISTEMA DE LOGGING DE ERRORES ---

def setup_logging():
    """Configura el sistema de registro de errores en un archivo."""
    if not config: return

    log_path = config.LOG_FILE_PATH

    # Configuración básica: Nivel ERROR o superior se guarda en archivo
    logging.basicConfig(
        filename=log_path,
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def log_error(message: str, exception: Exception = None):
    """Registra un error en el archivo log con el traceback."""
    if exception:
        logging.error(f"{message}\n{traceback.format_exc()}")
    else:
        logging.error(message)


def get_log_path() -> str:
    return config.LOG_FILE_PATH if config else "error.log"