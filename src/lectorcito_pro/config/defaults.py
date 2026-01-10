"""Defaults de configuración.

Objetivo:
- Separar los valores por defecto (plantilla) de la capa de persistencia (`store.py`).
- Mantener la *misma lógica de negocio* (mismas keys, mismos defaults).
- Evitar archivos "muertos": este módulo ahora es la fuente única de defaults.

Nota:
`store.py` sigue siendo el punto de entrada público (load/save),
pero construye DEFAULT_CONFIG usando `make_default_config(...)`.
"""

from __future__ import annotations

from typing import Iterable


def to_tags(items: Iterable[str]) -> list[dict]:
    """Convierte una lista/iterable de strings a lista de dicts con estado 'activo'."""
    return [{"nombre": str(item), "estado": "activo"} for item in items if str(item).strip()]


# --- Colecciones default (mantenidas desde v3/v5) ---
DEFAULT_IMPORTANT_FOLDERS = ["src"]

DEFAULT_INCLUDED_EXTENSIONS = [
    ".txt", ".py", ".html", ".java", ".md", ".css", ".js", ".json"
]

DEFAULT_EXCLUDED_FOLDERS = [
    "__pycache__", "env", "venv", ".venv", ".git", "build", "dist", ".idea"
]

DEFAULT_EXCLUDED_FILES = [
    "Pipfile.lock", "package.json", "package-lock.json"
]

DEFAULT_MEDIA_EXTENSIONS = [
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp", ".svg", ".ico",
    ".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm",
    ".mp3", ".wav", ".ogg", ".flac", ".m4a",
    ".zip", ".rar", ".7z", ".tar", ".gz",
    ".exe", ".dll", ".so", ".dylib",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".bak", ".tmp", ".log", ".dat",
    ".cer", ".crt", ".pem", ".key", ".pfx",
]


def make_default_config(default_lecturas_path: str) -> dict:
    """Crea el dict DEFAULT_CONFIG.

    `default_lecturas_path` se calcula en `store.py` porque depende del SO/usuario (appdirs).
    """
    return {
        "use_default_path": True,
        "custom_lecturas_path": "",
        "lecturas_path": default_lecturas_path,
        "last_read_folder": "",
        "theme": "Light",
        "language": "es",
        "etiquetas_carpetas_importantes": to_tags(DEFAULT_IMPORTANT_FOLDERS),
        "etiquetas_extensiones_incluidas": to_tags(DEFAULT_INCLUDED_EXTENSIONS),
        "etiquetas_carpetas_excluidas": to_tags(DEFAULT_EXCLUDED_FOLDERS),
        "etiquetas_archivos_excluidos": to_tags(DEFAULT_EXCLUDED_FILES),
        "media_extensions": list(DEFAULT_MEDIA_EXTENSIONS),
    }
