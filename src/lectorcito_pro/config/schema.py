"""Helpers de esquema/validación.

La lógica principal se mantiene en `config.store` para no alterar el comportamiento.
"""

from __future__ import annotations

from .store import DEFAULT_CONFIG


def merge_with_defaults(cfg: dict) -> dict:
    """Mezcla cualquier cfg parcial con DEFAULT_CONFIG (shallow merge)."""
    merged = DEFAULT_CONFIG.copy()
    merged.update(cfg or {})
    return merged
