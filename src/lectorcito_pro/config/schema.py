"""Esquema / normalización de configuración.

Este módulo se encarga de:
- Normalizar tags (lista de dicts: {nombre, estado}) incluso si vienen en formato legacy.
- Migrar keys específicas si el JSON viene "dañado" (casos reales detectados).
- Mezclar una cfg parcial con los defaults.

No cambia la lógica de negocio: solo evita estados inválidos y completa campos faltantes.
"""

from __future__ import annotations

from typing import Any

from .defaults import to_tags


TAG_KEYS = (
    "etiquetas_carpetas_importantes",
    "etiquetas_extensiones_incluidas",
    "etiquetas_carpetas_excluidas",
    "etiquetas_archivos_excluidos",
)


def _normalize_tag_dict(x: dict) -> dict:
    raw_name = x.get("nombre", "")

    # Recuperación de casos dañados: {"nombre": {"nombre": ".py", "estado": "activo"}, ...}
    if isinstance(raw_name, dict):
        raw_name = raw_name.get("nombre", "")

    raw_state = x.get("estado", "activo")
    if isinstance(raw_state, dict):
        raw_state = raw_state.get("estado", "activo")

    name = str(raw_name).strip()
    state = (raw_state or "activo") if isinstance(raw_state, str) else "activo"
    return {"nombre": name, "estado": state}


def ensure_tag_dicts(value: Any) -> Any:
    """Normaliza tags desde diferentes formatos a lista de dicts.

    Soporta:
    - Lista de dicts (moderno): normaliza campos.
    - Lista de strings (legacy): convierte a dicts {nombre, estado}.
    - Mixto: normaliza elemento por elemento.
    - Cualquier otra cosa: se devuelve sin tocar.
    """
    if not isinstance(value, list):
        return value

    if not value:
        return value

    # Caso moderno: lista de dicts
    if all(isinstance(x, dict) for x in value):
        return [_normalize_tag_dict(x) for x in value]

    # Caso legacy: lista de strings
    if all(isinstance(x, str) for x in value):
        return to_tags([x.strip() for x in value if x.strip()])

    # Caso mixto
    normalized: list[dict] = []
    for x in value:
        if isinstance(x, dict):
            normalized.append(_normalize_tag_dict(x))
        elif isinstance(x, str):
            name = x.strip()
            if name:
                normalized.append({"nombre": name, "estado": "activo"})
    return normalized


def migrate_config(config_data: dict) -> dict:
    """Aplica migraciones/normalizaciones in-place y retorna el dict."""
    if not isinstance(config_data, dict):
        return {}

    for key in TAG_KEYS:
        if key in config_data:
            config_data[key] = ensure_tag_dicts(config_data.get(key))
    return config_data


def merge_with_defaults(cfg: dict, defaults: dict) -> dict:
    """Mezcla cfg parcial con defaults (shallow)."""
    merged = dict(defaults or {})
    merged.update(cfg or {})
    return merged
