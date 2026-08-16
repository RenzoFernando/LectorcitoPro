import logging
import os
import platform
from logging.handlers import RotatingFileHandler

from app_meta import APP_VERSION

_LOGGER_NAME = "lectorcito"
_LOGGER = logging.getLogger(_LOGGER_NAME)
_LOGGER.propagate = False
_LOGGER.addHandler(logging.NullHandler())

def configure_logging(log_file_path: str, level: int = logging.INFO):
    clean_path = os.path.abspath(os.path.expanduser(str(log_file_path or "error.log")))
    _LOGGER.setLevel(level)

    for handler in list(_LOGGER.handlers):
        _LOGGER.removeHandler(handler)
        try:
            handler.close()
        except Exception:
            pass

    try:
        os.makedirs(os.path.dirname(clean_path), exist_ok=True)
        handler = RotatingFileHandler(
            clean_path,
            maxBytes=2 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8"
        )
    except OSError:
        _LOGGER.addHandler(logging.NullHandler())
        return ""

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | app=%(app_version)s | platform=%(platform_name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    _LOGGER.addHandler(handler)
    return clean_path

def _context_message(message: str, operation: str = "", file_path: str = "") -> str:
    parts = []
    if operation:
        parts.append(f"operation={operation}")
    if file_path:
        parts.append(f"file={file_path}")
    prefix = " | ".join(parts)
    text = str(message)
    return f"{prefix} | {text}" if prefix else text

def _extra() -> dict:
    return {
        "app_version": APP_VERSION,
        "platform_name": f"{platform.system()} {platform.release()}".strip()
    }

def log_info(message: str, operation: str = "", file_path: str = ""):
    _LOGGER.info(_context_message(message, operation, file_path), extra=_extra())

def log_warning(message: str, operation: str = "", file_path: str = ""):
    _LOGGER.warning(_context_message(message, operation, file_path), extra=_extra())

def log_error(message: str, exception: Exception = None, operation: str = "", file_path: str = ""):
    exc_info = None
    if exception is not None:
        exc_info = (type(exception), exception, exception.__traceback__)
    _LOGGER.error(
        _context_message(message, operation, file_path),
        exc_info=exc_info,
        extra=_extra()
    )

def get_logger() -> logging.Logger:
    return _LOGGER
