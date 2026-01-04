import logging
import os

from core.constants import LOGS_DIR

LOG_FILE = os.path.join(LOGS_DIR, "app.log")


def get_logger(name: str = "LectorcitoPro") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        os.makedirs(LOGS_DIR, exist_ok=True)
        handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def log_exception(exc: Exception):
    logger = get_logger()
    logger.exception("Unhandled exception: %s", exc)
