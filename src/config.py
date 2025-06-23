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
    """Convierte una lista de strings a la nueva estructura de etiquetas."""
    return [{"nombre": item, "estado": "activo"} for item in items]


# --- Configuración por Defecto (Nuevo Formato de Etiquetas) ---
DEFAULT_CONFIG = {
    "use_default_path": True,
    "custom_lecturas_path": "",
    "lecturas_path": DEFAULT_LECTURAS_PATH,
    "last_read_folder": "",
    "theme": "Light",
    "language": "es",

    # (Ver > Carpetas) Carpetas a resaltar.
    "etiquetas_carpetas_importantes": to_tags(
        ["src"]
    ),
    # (Ver > Archivos) Extensiones a incluir.
    "etiquetas_extensiones_incluidas": to_tags(
        [".txt", ".py", ".html", ".java", ".md", ".css", ".js", ".json"]
    ),
    # (No Ver > Carpetas) Carpetas a ignorar.
    "etiquetas_carpetas_excluidas": to_tags(
        ["__pycache__", "env", "venv", ".venv", "node_modules", ".git", "build", "dist", ".idea"]
    ),
    # (No Ver > Archivos) Nombres de archivo completos a ignorar.
    "etiquetas_archivos_excluidos": to_tags(
        [".spec", ".DS_Store", "Pipfile", "Pipfile.lock", "package.json", "package-lock.json"]
    ),

    # Los archivos multimedia siguen usando una lista simple porque no son configurables por el usuario.
    "media_extensions": [
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.ico', '.webp',
        '.mp4', '.mkv', '.avi', '.mov', '.webm',
        '.mp3', '.wav', '.flac', '.ogg',
        '.zip', '.rar', '.7z', '.tar', '.gz',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.exe', '.dll', '.bin', '.iso', '.so', '.dylib'
    ]
}


# --- Funciones de Manejo de Configuración ---

def _migrate_config(config_data: dict) -> dict:
    """Migra una configuración antigua al nuevo formato de etiquetas si es necesario."""
    migrated = False
    # Mapeo de claves antiguas a nuevas
    migration_map = {
        "important_folders": "etiquetas_carpetas_importantes",
        "text_extensions": "etiquetas_extensiones_incluidas",
        "excluded_folders": "etiquetas_carpetas_excluidas",
        "excluded_files": "etiquetas_archivos_excluidos",
    }
    for old_key, new_key in migration_map.items():
        if old_key in config_data and isinstance(config_data[old_key], list):
            # Si el primer elemento no es un diccionario, asumimos que es el formato antiguo
            if not config_data[old_key] or not isinstance(config_data[old_key][0], dict):
                config_data[new_key] = to_tags(config_data[old_key])
                del config_data[old_key]
                migrated = True
    if migrated:
        print("Configuración migrada al nuevo formato de etiquetas.")
    return config_data


def load_config() -> dict:
    """Carga la configuración desde JSON. Si no existe o está corrupto, usa los valores por defecto."""
    if os.path.exists(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, 'r', encoding="utf-8") as f:
                data = json.load(f)

            # Migrar si es un formato antiguo
            data = _migrate_config(data)

            # Asegura que todas las claves del DEFAULT_CONFIG existan en la configuración cargada.
            config_completa = DEFAULT_CONFIG.copy()
            config_completa.update(data)
            return config_completa
        except (json.JSONDecodeError, TypeError):
            # Si hay un error, se retorna una copia de la configuración por defecto.
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    """Guarda el diccionario de configuración actual en el archivo JSON."""
    try:
        # Crea una copia para no guardar claves que no deben persistir (como las de migración)
        config_to_save = DEFAULT_CONFIG.copy()
        config_to_save.update(config)

        with open(CONFIG_FILE_PATH, 'w', encoding="utf-8") as f:
            json.dump(config_to_save, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error al guardar la configuración: {e}")


def delete_config_file():
    """Elimina el archivo de configuración JSON si existe para restaurar los valores por defecto."""
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            os.remove(CONFIG_FILE_PATH)
    except Exception as e:
        print(f"Error al eliminar el archivo de configuración: {e}")
