import os
import json
from appdirs import user_config_dir

# --- Constantes de la Aplicación ---
APP_NAME = "LectorcitoPro"
APP_AUTHOR = "APPS_RenzoFernando"
CFG_NAME = "config.json"

# --- Rutas de Configuración ---
# Define el directorio de configuración del usuario usando appdirs para compatibilidad multiplataforma.
_config_dir = user_config_dir(APP_NAME, APP_AUTHOR, roaming=True)
os.makedirs(_config_dir, exist_ok=True)
CONFIG_FILE_PATH = os.path.join(_config_dir, CFG_NAME)

# Define y crea la ruta por defecto para guardar los reportes.
DEFAULT_LECTURAS_PATH = os.path.join(_config_dir, "Lecturas")
os.makedirs(DEFAULT_LECTURAS_PATH, exist_ok=True)


# --- Estructura de Etiqueta por Defecto ---
# Convierte una lista simple de strings a una lista de diccionarios para las etiquetas.
def to_tags(items: list[str]) -> list[dict]:
    return [{"nombre": item, "estado": "activo"} for item in items]


# --- Configuración por Defecto ---
# Diccionario con todos los ajustes predeterminados de la aplicación.
DEFAULT_CONFIG = {
    "use_default_path": True,
    "custom_lecturas_path": "",
    "lecturas_path": DEFAULT_LECTURAS_PATH,
    "last_read_folder": "",
    "theme": "Light",
    "language": "es",

    # Carpetas a resaltar en el reporte.
    "etiquetas_carpetas_importantes": to_tags(
        ["src"]
    ),
    # Extensiones de archivo a leer.
    "etiquetas_extensiones_incluidas": to_tags(
        [".txt", ".py", ".html", ".java", ".md", ".css", ".js", ".json"]
    ),
    # Carpetas a ignorar durante la lectura.
    "etiquetas_carpetas_excluidas": to_tags(
        ["__pycache__", "env", "venv", ".venv", ".git", "build", "dist", ".idea"]
    ),
    # Archivos específicos a ignorar por nombre.
    "etiquetas_archivos_excluidos": to_tags(
        ["Pipfile.lock", "package.json", "package-lock.json"]
    ),

    # Extensiones de archivos multimedia y otros binarios que no se deben leer.
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

# Migra una configuración de formato antiguo (listas simples) al nuevo formato (lista de etiquetas).
def _migrate_config(config_data: dict) -> dict:
    migrated = False
    migration_map = {
        "important_folders": "etiquetas_carpetas_importantes",
        "text_extensions": "etiquetas_extensiones_incluidas",
        "excluded_folders": "etiquetas_carpetas_excluidas",
        "excluded_files": "etiquetas_archivos_excluidos",
    }
    for old_key, new_key in migration_map.items():
        if old_key in config_data and isinstance(config_data[old_key], list):
            # Comprueba si la lista no está en el nuevo formato de diccionarios.
            if not config_data[old_key] or not isinstance(config_data[old_key][0], dict):
                config_data[new_key] = to_tags(config_data[old_key])
                del config_data[old_key]
                migrated = True
    if migrated:
        print("Configuración migrada al nuevo formato de etiquetas.")
    return config_data


# Carga la configuración desde el archivo JSON.
def load_config() -> dict:
    if os.path.exists(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, 'r', encoding="utf-8") as f:
                data = json.load(f)

            # Intenta migrar la configuración si es de un formato antiguo.
            data = _migrate_config(data)

            # Asegura que todas las claves por defecto existan en el archivo cargado.
            config_completa = DEFAULT_CONFIG.copy()
            config_completa.update(data)
            return config_completa
        except (json.JSONDecodeError, TypeError):
            # Si el archivo está corrupto, retorna la configuración por defecto.
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


# Guarda el diccionario de configuración en el archivo JSON.
def save_config(config: dict):
    try:
        # Usa una copia para asegurar que solo se guarden las claves relevantes.
        config_to_save = DEFAULT_CONFIG.copy()
        config_to_save.update(config)

        with open(CONFIG_FILE_PATH, 'w', encoding="utf-8") as f:
            json.dump(config_to_save, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error al guardar la configuración: {e}")


# Elimina el archivo de configuración para restaurar los valores por defecto.
def delete_config_file():
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            os.remove(CONFIG_FILE_PATH)
    except Exception as e:
        print(f"Error al eliminar el archivo de configuración: {e}")