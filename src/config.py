import os
import json
from appdirs import user_config_dir

# --- Constantes de Configuración ---
APP_NAME = "LectorcitoPro"
APP_AUTHOR = "RenzoFernando"
CFG_NAME = "config.json"

# --- Rutas de Configuración y Datos ---
# Directorio para el archivo config.json
_config_dir = user_config_dir(APP_NAME, APP_AUTHOR, roaming=True)
os.makedirs(_config_dir, exist_ok=True)
CONFIG_FILE_PATH = os.path.join(_config_dir, CFG_NAME)

# Directorio por defecto para las lecturas, junto al config.json
DEFAULT_LECTURAS_PATH = os.path.join(_config_dir, "Lecturas")
os.makedirs(DEFAULT_LECTURAS_PATH, exist_ok=True)

# --- Configuración por Defecto ---
DEFAULT_CONFIG = {
    "use_default_path": True,
    "custom_lecturas_path": "",
    "lecturas_path": DEFAULT_LECTURAS_PATH,
    "last_read_folder": "",

    "text_extensions": [".txt", ".py", ".html", ".java", ".md", ".css", ".js", ".json", ".xml", ".yml"],
    "excluded_folders": ["__pycache__", "venv", ".venv", "node_modules", ".git", "build", "dist", ".idea"],

    "media_extensions": [
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.ico', '.webp', '.tiff', '.tif',
        '.psd', '.ai', '.eps', '.heic', '.heif', '.avif', '.dng', '.cr2', '.cr3',
        '.nef', '.arw', '.orf', '.rw2', '.tga', '.exr', '.jxr', '.wdp',
        '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm',
        '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a',
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt',
        '.exe', '.dll', '.bin', '.iso'
    ],

    "theme": "Light",
    "language": "es"
}


# --- Funciones de Manejo ---
def load_config() -> dict:
    """Carga la configuración desde JSON, asegurando que todas las claves por defecto existan."""
    if os.path.exists(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, 'r', encoding="utf-8") as f:
                data = json.load(f)
            config_completa = DEFAULT_CONFIG.copy()
            config_completa.update(data)
            return config_completa
        except (json.JSONDecodeError, TypeError):
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    """Guarda el diccionario de configuración en el archivo JSON."""
    try:
        with open(CONFIG_FILE_PATH, 'w', encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error al guardar la configuración: {e}")
