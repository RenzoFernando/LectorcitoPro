
from __future__ import annotations


from dataclasses import dataclass
from typing import Any, Iterable


# Claves de configuración
KEY_IMPORTANT_FOLDERS = "etiquetas_carpetas_importantes"
KEY_INCLUDED_EXTS = "etiquetas_extensiones_incluidas"
KEY_EXCLUDED_FOLDERS = "etiquetas_carpetas_excluidas"
KEY_EXCLUDED_FILES = "etiquetas_archivos_excluidos"
KEY_MEDIA_EXTS = "media_extensions"


def active_tag_names(config: dict, key: str) -> set:
    """Devuelve el set de nombres de tags *activos* para una clave.

    Acepta tanto la estructura actual (lista de dicts) como una lista legacy de strings.
    """
    tag_list = (config or {}).get(key, []) or []
    active: set[str] = set()

    for item in tag_list:
        # Formato actual: {"nombre": "...", "estado": "activo"}
        if isinstance(item, dict):
            if item.get("estado") == "activo":
                name = str(item.get("nombre", "")).strip()
                if name:
                    active.add(name)
            continue

        # Formato legacy: ["src", ".py", ...]
        if isinstance(item, str):
            name = item.strip()
            if name:
                active.add(name)

    return active


@dataclass(frozen=True)
class ReportFilters:
    important_folders: set[str]
    included_extensions: set[str]
    media_extensions: set[str]
    excluded_folders: set[str]
    excluded_files: set[str]

    @property
    def all_valid_extensions(self) -> set[str]:
        return set(self.included_extensions).union(set(self.media_extensions))


def build_filters(config: dict) -> ReportFilters:
    """Construye un objeto de filtros desde el dict de configuración."""
    return ReportFilters(
        important_folders=active_tag_names(config, KEY_IMPORTANT_FOLDERS),
        included_extensions=active_tag_names(config, KEY_INCLUDED_EXTS),
        media_extensions=set((config or {}).get(KEY_MEDIA_EXTS, []) or []),
        excluded_folders=active_tag_names(config, KEY_EXCLUDED_FOLDERS),
        excluded_files=active_tag_names(config, KEY_EXCLUDED_FILES),
    )


def filename_matches_any_ext(filename: str, exts: Iterable[str]) -> bool:
    """True si `filename` termina en cualquiera de las extensiones dadas.
    """
    lower = filename.lower()
    return any(lower.endswith(ext) for ext in exts)
