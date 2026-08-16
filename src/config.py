import os
import json
import copy
from datetime import datetime
from app_meta import APP_NAME_INTERNAL, APP_VENDOR_NAME, APP_VERSION
from file_rules import normalize_file_rule_list, normalize_file_tag_list
from platform_services import get_platform_service
from app_logging import log_error, log_warning

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

_platform_service = get_platform_service()
_config_dir = _platform_service.get_user_config_dir(APP_NAME, APP_AUTHOR)
_data_dir = _platform_service.get_user_data_dir(APP_NAME, APP_AUTHOR)
_state_dir = _platform_service.get_user_state_dir(APP_NAME, APP_AUTHOR)

for _required_dir in (_config_dir, _data_dir, _state_dir):
    os.makedirs(_required_dir, exist_ok=True)

CONFIG_FILE_PATH = os.path.join(_config_dir, CFG_NAME)
LOG_FILE_PATH = os.path.join(_state_dir, LOG_NAME)
DEFAULT_LECTURAS_PATH = os.path.join(_data_dir, "Lecturas")
EXPORT_FILE_EXTENSION = ".json"
EXPORT_FORMAT_NAME = "lectorcito-pro-config"
EXPORT_SCHEMA_VERSION = 1

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
    normalized_profile["report_extension"] = ".txt" if str(normalized_profile.get("report_extension", ".md")).lower() == ".txt" else ".md"
    normalized_profile["use_gitignore_exclusions"] = bool(normalized_profile.get("use_gitignore_exclusions", False))
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
    "report_extension": ".md",
    "use_gitignore_exclusions": False,
    "etiquetas_carpetas_importantes": to_tags(["src"]),
    "etiquetas_extensiones_incluidas": to_tags([".txt", ".py", ".html", ".java", ".md", ".css", ".js", ".json", ".sql"]),
    "etiquetas_carpetas_excluidas": to_tags(["__pycache__", "env", "venv", ".venv", ".git", "build", "dist", ".idea"]),
    "etiquetas_archivos_excluidos": to_tags([
        "Pipfile.lock", "package.json", "package-lock.json",
        ".env", ".env.local", ".env.development", ".env.development.local",
        ".env.production", ".env.production.local", ".env.test", ".env.test.local",
        ".env.staging", ".env.staging.local", ".npmrc", ".pypirc", ".netrc"
    ]),
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
    "report_extension": ".md",
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

        except (json.JSONDecodeError, TypeError, OSError) as error:
            log_warning(
                str(error),
                operation="load_config",
                file_path=CONFIG_FILE_PATH
            )

    return build_runtime_config(
        profiles=base_structure.get("profiles", {}),
        active_id=base_structure.get("active_profile_id", "default")
    )


def build_persisted_config_payload(runtime_config: dict | None) -> dict:
    active_id = "default"
    if isinstance(runtime_config, dict):
        active_id = runtime_config.get("_active_profile_id", "default")
    profiles = clone_profiles_meta(runtime_config.get("_profiles_meta", {}) if isinstance(runtime_config, dict) else {})
    if isinstance(runtime_config, dict):
        profiles[active_id] = extract_profile_from_runtime_config(runtime_config, active_id)
    if active_id not in profiles:
        active_id = "default"
    return {
        "active_profile_id": active_id,
        "profiles": clone_profiles_meta(profiles)
    }


def build_export_config_package(runtime_config: dict | None) -> dict:
    return {
        "format": EXPORT_FORMAT_NAME,
        "schema_version": EXPORT_SCHEMA_VERSION,
        "app_name": APP_NAME_INTERNAL,
        "exported_from_version": APP_VERSION,
        "exported_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "data": build_persisted_config_payload(runtime_config)
    }


def export_config_to_file(file_path: str, runtime_config: dict | None):
    clean_path = str(file_path or "").strip()
    if not clean_path:
        raise ValueError("Ruta de exportación inválida.")
    package = build_export_config_package(runtime_config)
    output_dir = os.path.dirname(clean_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(clean_path, 'w', encoding="utf-8") as f:
        json.dump(package, f, indent=4, ensure_ascii=False)
    return clean_path


def _extract_import_payload(raw_data: dict | None) -> dict:
    if not isinstance(raw_data, dict):
        raise ValueError("El archivo no contiene una estructura JSON válida.")

    if raw_data.get("format") == EXPORT_FORMAT_NAME:
        payload = raw_data.get("data")
    elif "data" in raw_data and isinstance(raw_data.get("data"), dict) and "profiles" in raw_data.get("data", {}):
        payload = raw_data.get("data")
    else:
        payload = raw_data

    if not isinstance(payload, dict):
        raise ValueError("La configuración importada no contiene datos válidos.")

    profiles = payload.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise ValueError("La configuración importada no contiene perfiles válidos.")

    active_id = payload.get("active_profile_id", "default")
    if not isinstance(active_id, str) or not active_id.strip():
        active_id = "default"

    return {
        "active_profile_id": active_id.strip(),
        "profiles": clone_profiles_meta(profiles)
    }


def import_config_from_file(file_path: str) -> dict:
    clean_path = str(file_path or "").strip()
    if not clean_path:
        raise ValueError("Ruta de importación inválida.")
    with open(clean_path, 'r', encoding="utf-8") as f:
        raw_data = json.load(f)
    payload = _extract_import_payload(raw_data)
    return build_runtime_config(
        profiles=payload.get("profiles", {}),
        active_id=payload.get("active_profile_id", "default")
    )


def save_config(config: dict):
    try:
        final_json = build_persisted_config_payload(config)

        with open(CONFIG_FILE_PATH, 'w', encoding="utf-8") as f:
            json.dump(final_json, f, indent=4, ensure_ascii=False)

    except Exception as e:
        log_error(
            "Error al guardar config.",
            e,
            operation="save_config",
            file_path=CONFIG_FILE_PATH
        )


def delete_config_file():
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            os.remove(CONFIG_FILE_PATH)
    except Exception as e:
        log_error(
            "Error eliminando config.",
            e,
            operation="delete_config",
            file_path=CONFIG_FILE_PATH
        )