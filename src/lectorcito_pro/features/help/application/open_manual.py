from __future__ import annotations

"""Caso de uso: obtener ruta del manual (infografía).

La UI muestra una imagen (Infografía_LectorcitoPro.png) dentro de un diálogo.
Este módulo centraliza el nombre del recurso y la resolución de rutas, para
evitar que la UI tenga literales duplicados.
"""

import os

from ....core.paths import resource_path

INFOGRAPHIC_FILENAME = "Infografía_LectorcitoPro.png"


def get_infographic_path() -> str:
    """Devuelve la ruta absoluta al archivo de la infografía."""
    return resource_path(INFOGRAPHIC_FILENAME)


def infographic_exists() -> bool:
    """True si la infografía existe en el bundle/recursos."""
    return os.path.exists(get_infographic_path())
