import os
import json
import copy
from appdirs import user_config_dir
from app_meta import APP_NAME_INTERNAL, APP_VENDOR_NAME
from file_rules import normalize_file_rule_list, normalize_file_tag_list

PROFILE_CONFIG_KEYS = (
    "use_default_path",
    "custom_lecturas_path",
    "custom_exe_path",
    "lecturas_path",
    "last_read_folder",
    "theme",
    "language",
    "report_extension",
    "use_gitignore_exclusions",
    "etiquetas_carpetas_importantes",
    "etiquetas_extensiones_incluidas",
    "etiquetas_carpetas_excluidas",
    "etiquetas_archivos_excluidos",
    "media_extensions",
    "etiquetas_multimedia_config"
)

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
    normalized_profile = copy.deepcopy(profile) if isinstance(profile, dict) else {}
    normalized_profile["use_default_path"] = bool(normalized_profile.get("use_default_path", True))
    normalized_profile["custom_lecturas_path"] = str(normalized_profile.get("custom_lecturas_path", "") or "")
    normalized_profile["custom_exe_path"] = str(normalized_profile.get("custom_exe_path", "") or "")
    normalized_profile["lecturas_path"] = str(normalized_profile.get("lecturas_path", DEFAULT_LECTURAS_PATH) or DEFAULT_LECTURAS_PATH)
    normalized_profile["last_read_folder"] = str(normalized_profile.get("last_read_folder", "") or "")
    normalized_profile["theme"] = "Dark" if str(normalized_profile.get("theme", "Light")).lower() == "dark" else "Light"
    normalized_profile["language"] = "en" if str(normalized_profile.get("language", "es")).lower() == "en" else "es"
    normalized_profile["report_extension"] = ".md" if str(normalized_profile.get("report_extension", ".txt")).lower() == ".md" else ".txt"
    normalized_profile["use_gitignore_exclusions"] = bool(
        normalized_profile.get("use_gitignore_exclusions", False)
    )
    normalized_profile["etiquetas_carpetas_importantes"] = normalize_file_tag_list(
        normalized_profile.get("etiquetas_carpetas_importantes", [])
    )
    normalized_profile["etiquetas_extensiones_incluidas"] = normalize_file_tag_list(
        normalized_profile.get("etiquetas_extensiones_incluidas", [])
    )
    normalized_profile["etiquetas_carpetas_excluidas"] = normalize_file_tag_list(
        normalized_profile.get("etiquetas_carpetas_excluidas", [])
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


def _copy_profile_payload(profile: dict | None) -> dict:
    source = profile if isinstance(profile, dict) else {}
    clean_profile = {}
    for key in PROFILE_CONFIG_KEYS:
        if key in source:
            clean_profile[key] = copy.deepcopy(source.get(key))
    return clean_profile


def _get_profile_base(profile_id: str) -> dict:
    if profile_id == "default":
        return copy.deepcopy(DEFAULT_CONFIG_VALUES)
    return copy.deepcopy(BLANK_PROFILE_CONFIG)


def build_profile_config(profile: dict | None, profile_id: str = "default") -> dict:
    normalized_profile = _get_profile_base(profile_id)
    normalized_profile.update(_copy_profile_payload(profile))
    return _normalize_profile_file_rules(normalized_profile)


def extract_profile_from_runtime_config(runtime_config: dict | None, profile_id: str = "default") -> dict:
    return build_profile_config(_copy_profile_payload(runtime_config), profile_id)


def clone_profiles_meta(profiles: dict | None) -> dict:
    normalized_profiles = {}
    source = profiles if isinstance(profiles, dict) else {}
    for profile_id, profile_data in source.items():
        if isinstance(profile_data, dict):
            normalized_profiles[profile_id] = build_profile_config(profile_data, profile_id)
        else:
            normalized_profiles[profile_id] = profile_data
    if "default" not in normalized_profiles:
        normalized_profiles["default"] = build_profile_config(DEFAULT_CONFIG_VALUES, "default")
    return normalized_profiles


def build_runtime_config(profiles: dict | None = None, active_id: str = "default") -> dict:
    normalized_profiles = clone_profiles_meta(profiles)
    resolved_active_id = active_id if active_id in normalized_profiles else "default"
    runtime_config = build_profile_config(normalized_profiles.get(resolved_active_id, {}), resolved_active_id)
    runtime_config["_profiles_meta"] = clone_profiles_meta(normalized_profiles)
    runtime_config["_active_profile_id"] = resolved_active_id
    return runtime_config


def _normalize_profiles_meta(profiles: dict) -> dict:
    return clone_profiles_meta(profiles)


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
    "use_gitignore_exclusions": False,
    "etiquetas_carpetas_importantes": to_tags(["src"]),
    "etiquetas_extensiones_incluidas": to_tags([".txt", ".py", ".html", ".java", ".md", ".css", ".js", ".json", ".sql"]),
    "etiquetas_carpetas_excluidas": to_tags(["__pycache__", "env", "venv", ".venv", ".git", "build", "dist", ".idea"]),
    "etiquetas_archivos_excluidos": to_tags(["Pipfile.lock", "package.json", "package-lock.json"]),
    "media_extensions": [
        '.png', '.jpg', '.gif', '.ico',
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
    "use_gitignore_exclusions": False,
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
    return build_profile_config(BLANK_PROFILE_CONFIG, "new")


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
                    base_structure["profiles"]["default"] = build_profile_config(migrated_data, "default")
                    base_structure["active_profile_id"] = "default"

        except (json.JSONDecodeError, TypeError):
            print("Error leyendo config, usando defaults.")

    return build_runtime_config(
        profiles=base_structure.get("profiles", {}),
        active_id=base_structure.get("active_profile_id", "default")
    )


def save_config(config: dict):
    try:
        active_id = config.get("_active_profile_id", "default")
        profiles = clone_profiles_meta(config.get("_profiles_meta", {"default": copy.deepcopy(DEFAULT_CONFIG_VALUES)}))
        profiles[active_id] = extract_profile_from_runtime_config(config, active_id)

        final_json = {
            "active_profile_id": active_id if active_id in profiles else "default",
            "profiles": clone_profiles_meta(profiles)
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