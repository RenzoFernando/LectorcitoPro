import os

from app_logging import configure_logging, log_error as _log_error, log_info as _log_info, log_warning as _log_warning
from runtime_context import get_resource_base_candidates

try:
    import config
except ImportError:
    config = None


# =============================================================================
# GESTION DE RECURSOS
# =============================================================================

def resource_path(relative_path: str) -> str:
    normalized_relative = os.path.normpath(str(relative_path or "").lstrip("\\/"))
    candidates = get_resource_base_candidates(__file__)

    for base_path in candidates:
        # PyInstaller crea una carpeta temporal en _MEIPASS
        candidate = os.path.join(base_path, "resources", normalized_relative)
        if os.path.exists(candidate):
            return candidate

        # Nuitka o Modo Desarrollo
        alternate = os.path.join(base_path, normalized_relative)
        # Si estamos en 'src', los resources suelen estar un nivel arriba
        if os.path.basename(base_path) == 'src':
            alternate = os.path.join(os.path.abspath(os.path.join(base_path, "..")), "resources", normalized_relative)
        # Nuitka mantiene la estructura interna 'src' al compilar
        if os.path.exists(alternate):
            return alternate

    return os.path.join(candidates[0], "resources", normalized_relative)


# =============================================================================
# SISTEMA DE LOGS
# =============================================================================

def setup_logging():
    if not config:
        return
    configure_logging(config.LOG_FILE_PATH)


def log_error(message: str, exception: Exception = None, operation: str = "", file_path: str = ""):
    _log_error(message, exception, operation=operation, file_path=file_path)


def log_warning(message: str, operation: str = "", file_path: str = ""):
    _log_warning(message, operation=operation, file_path=file_path)


def log_info(message: str, operation: str = "", file_path: str = ""):
    _log_info(message, operation=operation, file_path=file_path)


def get_log_path() -> str:
    return config.LOG_FILE_PATH if config else "error.log"
