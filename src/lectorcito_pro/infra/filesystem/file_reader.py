from __future__ import annotations

import os
from typing import Optional, Tuple


def read_text_file(file_path: str, encoding: str = "utf-8") -> Tuple[str, Optional[str]]:
    """Lee un archivo de texto de forma segura.

    Retorna:
        (contenido, None) si pudo leerlo
        ("", mensaje_error) si falló

    Nota: Mantiene el enfoque de la app: reportar errores sin romper el proceso.
    """
    try:
        with open(file_path, "r", encoding=encoding, errors="replace") as f:
            return f.read(), None
    except Exception as e:
        return "", f"No se pudo leer el archivo '{file_path}': {e}"


def describe_media_file(file_path: str) -> str:
    """Devuelve una línea descriptiva para archivos multimedia omitidos."""
    name = os.path.basename(file_path)
    ext = os.path.splitext(name)[1].lower()
    return f"(multimedia omitido) {name} ({ext})"
