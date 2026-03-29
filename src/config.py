import os
import json
import copy
from appdirs import user_config_dir
from app_meta import APP_NAME_INTERNAL, APP_VENDOR_NAME
from file_rules import normalize_file_rule_list, normalize_file_tag_list

# =============================================================================
# CONFIGURACION DEL SISTEMA
# =============================================================================

APP_NAME = APP_NAME_INTERNAL
APP_AUTHOR = APP_VENDOR_NAME
CFG_NAME = "config.json"
LOG_NAME = "error.log"

_config_dir = user_config_dir(APP_NAME, APP_AUTHOR, roaming=True)
os.makedirs(_config_dir, exist_ok=True)

CONFIG_FILE_PATH = os.path.join(_config_dir, CFG_NAME)
LOG_FILE_PATH = os.path.join(_config_dir, LOG_NAME)
DEFAULT_LECTURAS_PATH = os.path.join(_config_dir, "Lecturas")

os.makedirs(DEFAULT_LECTURAS_PATH, exist_ok=True)


def to_tags(items: list[str]) -> list[dict]:
    return [{"nombre": item, "estado": "activo"} for item in items]


def _normalize_profile_file_rules(profile: dict) -> dict:
    normalized_profile = copy.deepcopy(profile)
    normalized_profile["etiquetas_extensiones_incluidas"] = normalize_file_tag_list(
        normalized_profile.get("etiquetas_extensiones_incluidas", [])
    )
    normalized_profile["etiquetas_archivos_excluidos"] = normalize_file_tag_list(
        normalized_profile.get("etiquetas_archivos_excluidos", [])
    )
    normalized_profile["etiquetas_multimedia_config"] = normalize_file_tag_list(
        normalized_profile.get("etiquetas_multimedia_config", [])
    )
    normalized_profile["media_extensions"] = normalize_file_rule_list(
        normalized_profile.get("media_extensions", [])
    )
    return normalized_profile


def _normalize_profiles_meta(profiles: dict) -> dict:
    normalized_profiles = {}
    for profile_id, profile_data in profiles.items():
        if isinstance(profile_data, dict):
            normalized_profiles[profile_id] = _normalize_profile_file_rules(profile_data)
        else:
            normalized_profiles[profile_id] = profile_data
    return normalized_profiles


# =============================================================================
# PERFILES Y VALORES POR DEFECTO
# =============================================================================

DEFAULT_CONFIG_VALUES = {
    "use_default_path": True,
    "custom_lecturas_path": "",
    "custom_exe_path": "",
    "lecturas_path": DEFAULT_LECTURAS_PATH,
    "last_read_folder": "",
    "theme": "Light",
    "language": "es",
    "report_extension": ".txt",
    "etiquetas_carpetas_importantes": to_tags(["src"]),
    "etiquetas_extensiones_incluidas": to_tags([".txt", ".py", ".html", ".java", ".md", ".css", ".js", ".json", ".sql"]),
    "etiquetas_carpetas_excluidas": to_tags(["__pycache__", "env", "venv", ".venv", ".git", "build", "dist", ".idea"]),
    "etiquetas_archivos_excluidos": to_tags(["Pipfile.lock", "package.json", "package-lock.json"]),
    "media_extensions": [
        '.png', '.jpg', '.gif', '.svg', '.ico',
        '.mp4', '.mkv', '.avi',
        '.mp3', '.wav',
        '.zip', '.rar', '.7z',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.exe', '.bin', '.iso', ".pfx"
    ],
    "etiquetas_multimedia_config": []
}

BLANK_PROFILE_CONFIG = {
    "use_default_path": True,
    "custom_lecturas_path": "",
    "custom_exe_path": "",
    "lecturas_path": DEFAULT_LECTURAS_PATH,
    "last_read_folder": "",
    "theme": "Light",
    "language": "es",
    "report_extension": ".txt",
    "etiquetas_carpetas_importantes": [],
    "etiquetas_extensiones_incluidas": [],
    "etiquetas_carpetas_excluidas": [],
    "etiquetas_archivos_excluidos": [],
    "media_extensions": [],
    "etiquetas_multimedia_config": []
}

DEFAULT_CONFIG_VALUES = _normalize_profile_file_rules(DEFAULT_CONFIG_VALUES)
BLANK_PROFILE_CONFIG = _normalize_profile_file_rules(BLANK_PROFILE_CONFIG)


# =============================================================================
# LOGICA DE CARGA Y GUARDADO
# =============================================================================

def _migrate_old_keys(data: dict) -> dict:
    migration_map = {
        "important_folders": "etiquetas_carpetas_importantes",
        "text_extensions": "etiquetas_extensiones_incluidas",
        "excluded_folders": "etiquetas_carpetas_excluidas",
        "excluded_files": "etiquetas_archivos_excluidos",
    }
    for old_key, new_key in migration_map.items():
        if old_key in data and isinstance(data[old_key], list):
            if not data[old_key] or not isinstance(data[old_key][0], dict):
                data[new_key] = to_tags(data[old_key])
                del data[old_key]
    return data


def get_blank_profile() -> dict:
    return copy.deepcopy(BLANK_PROFILE_CONFIG)


def load_config() -> dict:
    base_structure = {
        "active_profile_id": "default",
        "profiles": {
            "default": copy.deepcopy(DEFAULT_CONFIG_VALUES)
        }
    }

    if os.path.exists(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, 'r', encoding="utf-8") as f:
                loaded_data = json.load(f)

                if "profiles" in loaded_data:
                    base_structure = loaded_data
                else:
                    migrated_data = _migrate_old_keys(loaded_data)
                    full_default = copy.deepcopy(DEFAULT_CONFIG_VALUES)
                    full_default.update(migrated_data)
                    base_structure["profiles"]["default"] = full_default
                    base_structure["active_profile_id"] = "default"

        except (json.JSONDecodeError, TypeError):
            print("Error leyendo config, usando defaults.")

    active_id = base_structure.get("active_profile_id", "default")
    if active_id not in base_structure["profiles"]:
        active_id = "default"

    if "default" not in base_structure["profiles"]:
        base_structure["profiles"]["default"] = copy.deepcopy(DEFAULT_CONFIG_VALUES)

    base_structure["profiles"] = _normalize_profiles_meta(base_structure["profiles"])
    active_data = base_structure["profiles"][active_id]

    if active_id == "default":
        config_completa = copy.deepcopy(DEFAULT_CONFIG_VALUES)
        config_completa.update(active_data)
    else:
        config_completa = copy.deepcopy(BLANK_PROFILE_CONFIG)
        config_completa.update(active_data)

    config_completa = _normalize_profile_file_rules(config_completa)
    config_completa["_profiles_meta"] = base_structure["profiles"]
    config_completa["_active_profile_id"] = active_id

    return config_completa


def save_config(config: dict):
    try:
        profiles = config.get("_profiles_meta", {"default": copy.deepcopy(DEFAULT_CONFIG_VALUES)})
        profiles = _normalize_profiles_meta(profiles)
        active_id = config.get("_active_profile_id", "default")

        current_profile_data = config.copy()
        if "_profiles_meta" in current_profile_data: del current_profile_data["_profiles_meta"]
        if "_active_profile_id" in current_profile_data: del current_profile_data["_active_profile_id"]

        current_profile_data = _normalize_profile_file_rules(current_profile_data)
        profiles[active_id] = current_profile_data

        final_json = {
            "active_profile_id": active_id,
            "profiles": profiles
        }

        with open(CONFIG_FILE_PATH, 'w', encoding="utf-8") as f:
            json.dump(final_json, f, indent=4, ensure_ascii=False)

    except Exception as e:
        print(f"Error al guardar config: {e}")


def delete_config_file():
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            os.remove(CONFIG_FILE_PATH)
    except Exception as e:
        print(f"Error eliminando config: {e}")
