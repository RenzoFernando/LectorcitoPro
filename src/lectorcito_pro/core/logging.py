
import logging


def configure_logging(level: int = logging.INFO) -> None:
    """Configura logging básico. (Hook para futuro)"""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
