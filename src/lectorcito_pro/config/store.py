from __future__ import annotations

import json
import os
from typing import Any

from appdirs import user_config_dir

from ..core.constants import APP_AUTHOR, APP_NAME, CFG_NAME
from ..core.errors import ConfigError
from .defaults import make_default_config, to_tags
from .schema import merge_with_defaults, migrate_config


# --- Rutas de Configuración ---
CONFIG_DIR = user_config_dir(APP_NAME, APP_AUTHOR, roaming=True)
os.makedirs(CONFIG_DIR, exist_ok=True)
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR, CFG_NAME)

# Ruta por defecto para guardar reportes
DEFAULT_LECTURAS_PATH = os.path.join(CONFIG_DIR, "Lecturas")
os.makedirs(DEFAULT_LECTURAS_PATH, exist_ok=True)

# --- Configuración por Defecto ---
DEFAULT_CONFIG = make_default_config(DEFAULT_LECTURAS_PATH)


def _load_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data: Any = json.load(f)
        if not isinstance(data, dict):
            raise ConfigError("El archivo de configuración no contiene un objeto JSON válido.")
        return data
    except json.JSONDecodeError as e:
        raise ConfigError(f"JSON inválido en {path}: {e}") from e
    except OSError as e:
        raise ConfigError(f"No se pudo leer {path}: {e}") from e


def load_config() -> dict:
    """Carga la configuración desde disco y hace merge con DEFAULT_CONFIG.

    Mantiene el comportamiento original:
    - Si hay error leyendo/parsing, no rompe la app: vuelve a DEFAULT_CONFIG.
    - Normaliza tags legacy/dañados para evitar errores en UI/filters.
    """
    if os.path.exists(CONFIG_FILE_PATH):
        try:
            config_data = _load_json(CONFIG_FILE_PATH)
            config_data = migrate_config(config_data)
            return merge_with_defaults(config_data, DEFAULT_CONFIG)
        except ConfigError as e:
            # No cambiamos la lógica: sólo informamos y volvemos a defaults
            print(f"[ConfigError] {e}")
        except Exception as e:
            # Fallback ultra defensivo
            print(f"[Error] No se pudo cargar la configuración: {e}")

    return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> None:
    """Guarda la configuración a disco."""
    try:
        config_to_save = DEFAULT_CONFIG.copy()
        config_to_save.update(config or {})

        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(config_to_save, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"[Error] No se pudo guardar la configuración: {e}")


def delete_config_file() -> None:
    """Elimina el archivo de configuración si existe."""
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            os.remove(CONFIG_FILE_PATH)
    except Exception as e:
        print(f"[Error] No se pudo eliminar el archivo de configuración: {e}")
