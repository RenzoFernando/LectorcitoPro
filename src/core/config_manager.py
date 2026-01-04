import json
import os
from typing import Dict, Iterable

from appdirs import user_config_dir

from core.constants import APP_AUTHOR, APP_NAME
from domain.settings import AppSettings, Tag

CFG_NAME = "config.json"

_config_dir = user_config_dir(APP_NAME, APP_AUTHOR, roaming=True)
os.makedirs(_config_dir, exist_ok=True)
CONFIG_FILE_PATH = os.path.join(_config_dir, CFG_NAME)

DEFAULT_LECTURAS_PATH = os.path.join(_config_dir, "Lecturas")
os.makedirs(DEFAULT_LECTURAS_PATH, exist_ok=True)


def _to_tags(items: Iterable[str]):
    return [tag.to_dict() for tag in Tag.from_iterable(items)]


DEFAULT_CONFIG: Dict = {
    "use_default_path": True,
    "custom_lecturas_path": "",
    "lecturas_path": DEFAULT_LECTURAS_PATH,
    "last_read_folder": "",
    "theme": "Light",
    "language": "es",
    "etiquetas_carpetas_importantes": _to_tags(["src"]),
    "etiquetas_extensiones_incluidas": _to_tags([".txt", ".py", ".html", ".java", ".md", ".css", ".js", ".json"]),
    "etiquetas_carpetas_excluidas": _to_tags(["__pycache__", "env", "venv", ".venv", ".git", "build", "dist", ".idea"]),
    "etiquetas_archivos_excluidos": _to_tags(["Pipfile.lock", "package.json", "package-lock.json"]),
    "media_extensions": [
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.ico', '.webp',
        '.mp4', '.mkv', '.avi', '.mov', '.webm',
        '.mp3', '.wav', '.flac', '.ogg',
        '.zip', '.rar', '.7z', '.tar', '.gz',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.exe', '.dll', '.bin', '.iso', '.so', '.dylib', ".cer", ".pfx"
    ]
}


def _migrate_config(config_data: Dict) -> Dict:
    migrated = False
    migration_map = {
        "important_folders": "etiquetas_carpetas_importantes",
        "text_extensions": "etiquetas_extensiones_incluidas",
        "excluded_folders": "etiquetas_carpetas_excluidas",
        "excluded_files": "etiquetas_archivos_excluidos",
    }
    for old_key, new_key in migration_map.items():
        if old_key in config_data and isinstance(config_data[old_key], list):
            if not config_data[old_key] or not isinstance(config_data[old_key][0], dict):
                config_data[new_key] = _to_tags(config_data[old_key])
                del config_data[old_key]
                migrated = True
    if migrated:
        print("Configuración migrada al nuevo formato de etiquetas.")
    return config_data


def load_config() -> AppSettings:
    if os.path.exists(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, 'r', encoding="utf-8") as f:
                data = json.load(f)
            data = _migrate_config(data)
            cfg = DEFAULT_CONFIG.copy()
            cfg.update(data)
            return AppSettings.from_dict(cfg)
        except (json.JSONDecodeError, TypeError):
            return AppSettings.from_dict(DEFAULT_CONFIG)
    return AppSettings.from_dict(DEFAULT_CONFIG)


def save_config(config: AppSettings | Dict):
    try:
        cfg_dict = config.to_dict() if isinstance(config, AppSettings) else dict(config)
        config_to_save = DEFAULT_CONFIG.copy()
        config_to_save.update(cfg_dict)
        with open(CONFIG_FILE_PATH, 'w', encoding="utf-8") as f:
            json.dump(config_to_save, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error al guardar la configuración: {e}")


def delete_config_file():
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            os.remove(CONFIG_FILE_PATH)
    except Exception as e:
        print(f"Error al eliminar el archivo de configuración: {e}")
