import os
import json
from appdirs import user_config_dir

# --- Constantes de la Aplicación ---
APP_NAME = "LectorcitoPro"
APP_AUTHOR = "APPS_RenzoFernando"
CFG_NAME = "config.json"

# --- Rutas de Configuración ---
_config_dir = user_config_dir(APP_NAME, APP_AUTHOR, roaming=True)
os.makedirs(_config_dir, exist_ok=True)
CONFIG_FILE_PATH = os.path.join(_config_dir, CFG_NAME)

DEFAULT_LECTURAS_PATH = os.path.join(_config_dir, "Lecturas")
os.makedirs(DEFAULT_LECTURAS_PATH, exist_ok=True)


# --- Estructura de Etiqueta por Defecto ---
def to_tags(items: list[str]) -> list[dict]:
    return [{"nombre": item, "estado": "activo"} for item in items]


# --- Configuración Base (Full Default) ---
# Esta es la configuración completa típica con filtros pre-cargados (para el perfil Default inicial).
DEFAULT_CONFIG_VALUES = {
    "use_default_path": True,
    "custom_lecturas_path": "",
    "lecturas_path": DEFAULT_LECTURAS_PATH,
    "last_read_folder": "",
    "theme": "Light",
    "language": "es",

    "etiquetas_carpetas_importantes": to_tags(["src"]),
    "etiquetas_extensiones_incluidas": to_tags([".txt", ".py", ".html", ".java", ".md", ".css", ".js", ".json"]),
    "etiquetas_carpetas_excluidas": to_tags(["__pycache__", "env", "venv", ".venv", ".git", "build", "dist", ".idea"]),
    "etiquetas_archivos_excluidos": to_tags(["Pipfile.lock", "package.json", "package-lock.json"]),

    "media_extensions": [
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.ico', '.webp',
        '.mp4', '.mkv', '.avi', '.mov', '.webm',
        '.mp3', '.wav', '.flac', '.ogg',
        '.zip', '.rar', '.7z', '.tar', '.gz',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.exe', '.dll', '.bin', '.iso', '.so', '.dylib', ".cer", ".pfx"
    ],
    "etiquetas_multimedia_config": []
}

# --- Configuración "En Blanco" (Blank Slate) ---
# CAMBIO: Ahora TODO está vacío, incluidas las extensiones multimedia.
BLANK_PROFILE_CONFIG = {
    "use_default_path": True,
    "custom_lecturas_path": "",
    "lecturas_path": DEFAULT_LECTURAS_PATH,
    "last_read_folder": "",
    "theme": "Light",  # Por defecto claro
    "language": "es",  # Por defecto español

    # Listas vacías para que el usuario personalice desde cero
    "etiquetas_carpetas_importantes": [],
    "etiquetas_extensiones_incluidas": [],
    "etiquetas_carpetas_excluidas": [],
    "etiquetas_archivos_excluidos": [],

    # CAMBIO: Multimedia totalmente vacío
    "media_extensions": [],
    "etiquetas_multimedia_config": []
}


# --- Funciones de Migración y Manejo ---

def _migrate_old_keys(data: dict) -> dict:
    """Migra claves antiguas (listas planas) al formato de etiquetas."""
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
    """Retorna una copia de la configuración en blanco."""
    return BLANK_PROFILE_CONFIG.copy()


def load_config() -> dict:
    """
    Carga la configuración.
    Retorna un diccionario que representa el PERFIL ACTIVO, pero inyecta metadata oculta.
    """
    base_structure = {
        "active_profile_id": "default",
        "profiles": {
            "default": DEFAULT_CONFIG_VALUES.copy()
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
                full_default = DEFAULT_CONFIG_VALUES.copy()
                full_default.update(migrated_data)

                base_structure["profiles"]["default"] = full_default
                base_structure["active_profile_id"] = "default"

        except (json.JSONDecodeError, TypeError):
            print("Error leyendo config, usando defaults.")

    active_id = base_structure.get("active_profile_id", "default")
    if active_id not in base_structure["profiles"]:
        active_id = "default"
        if "default" not in base_structure["profiles"]:
            base_structure["profiles"]["default"] = DEFAULT_CONFIG_VALUES.copy()

    active_data = base_structure["profiles"][active_id]

    # Aseguramos claves mínimas
    if active_id == "default":
        config_completa = DEFAULT_CONFIG_VALUES.copy()
        config_completa.update(active_data)
    else:
        # Para perfiles custom, usamos la base BLANK + datos guardados
        config_completa = BLANK_PROFILE_CONFIG.copy()
        config_completa.update(active_data)

    config_completa["_profiles_meta"] = base_structure["profiles"]
    config_completa["_active_profile_id"] = active_id

    return config_completa


def save_config(config: dict):
    """
    Guarda la configuración reconstruyendo el JSON global.
    """
    try:
        profiles = config.get("_profiles_meta", {"default": DEFAULT_CONFIG_VALUES.copy()})
        active_id = config.get("_active_profile_id", "default")

        # Limpiar metadata del perfil actual antes de guardar
        current_profile_data = config.copy()
        if "_profiles_meta" in current_profile_data: del current_profile_data["_profiles_meta"]
        if "_active_profile_id" in current_profile_data: del current_profile_data["_active_profile_id"]

        profiles[active_id] = current_profile_data

        final_json = {
            "active_profile_id": active_id,
            "profiles": profiles
        }

        with open(CONFIG_FILE_PATH, 'w', encoding="utf-8") as f:
            json.dump(final_json, f, indent=4, ensure_ascii=False)

    except Exception as e:
        print(f"Error al guardar la configuración: {e}")


def delete_config_file():
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            os.remove(CONFIG_FILE_PATH)
    except Exception as e:
        print(f"Error al eliminar el archivo de configuración: {e}")