from __future__ import annotations

"""Caso de uso: actualizar/normalizar filtros.

En la app, los filtros se guardan como listas de dicts:
    {"nombre": "src", "estado": "activo"}

Este módulo ofrece helpers para normalizar entradas sin cambiar lógica de negocio.
"""

from typing import Iterable


def normalize_extension_tags(tags: list[dict]) -> list[dict]:
    """Asegura que todas las extensiones empiecen con '.' (como en la UI original)."""
    for tag in tags or []:
        nombre = str(tag.get("nombre", "")).strip()
        if nombre and not nombre.startswith("."):
            tag["nombre"] = f".{nombre}"
    return tags


def as_tags(items: Iterable[str]) -> list[dict]:
    """Convierte strings a estructura de tags activa."""
    return [{"nombre": str(it).strip(), "estado": "activo"} for it in items if str(it).strip()]
