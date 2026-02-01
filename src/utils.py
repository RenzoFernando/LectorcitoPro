import sys
import os
import logging
import traceback

try:
    import config
except ImportError:
    config = None


# =============================================================================
# GESTION DE RECURSOS
# =============================================================================

def resource_path(relative_path: str) -> str:
    try:
        # PyInstaller crea una carpeta temporal en _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    return os.path.join(base_path, 'recursos', relative_path)


# =============================================================================
# SISTEMA DE LOGS
# =============================================================================

def setup_logging():
    if not config: return

    logging.basicConfig(
        filename=config.LOG_FILE_PATH,
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def log_error(message: str, exception: Exception = None):
    if exception:
        logging.error(f"{message}\n{traceback.format_exc()}")
    else:
        logging.error(message)


def get_log_path() -> str:
    return config.LOG_FILE_PATH if config else "error.log"