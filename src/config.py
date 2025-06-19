import os
import json
from appdirs import user_config_dir

# --- Constantes de la Aplicación ---
APP_NAME = "LectorcitoPro"
APP_AUTHOR = "RenzoFernando"
CFG_NAME = "config.json"

# --- Rutas de Configuración ---
_config_dir = user_config_dir(APP_NAME, APP_AUTHOR, roaming=True)
os.makedirs(_config_dir, exist_ok=True)
CONFIG_FILE_PATH = os.path.join(_config_dir, CFG_NAME)

DEFAULT_LECTURAS_PATH = os.path.join(_config_dir, "Lecturas")
os.makedirs(DEFAULT_LECTURAS_PATH, exist_ok=True)

# --- Configuración por Defecto ---
DEFAULT_CONFIG = {
    "use_default_path": True,
    "custom_lecturas_path": "",
    "lecturas_path": DEFAULT_LECTURAS_PATH,
    "last_read_folder": "",
    "text_extensions": [".txt", ".py", ".html", ".java", ".md", ".css", ".js", ".json", ".xml", ".yml", ".bat", ".ps1"],
    "excluded_folders": ["__pycache__", "venv", ".venv", "node_modules", ".git", "build", "dist", ".idea"],
    "media_extensions": [
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.ico', '.webp',
        '.mp4', '.mkv', '.avi', '.mov', '.webm',
        '.mp3', '.wav', '.flac', '.ogg',
        '.zip', '.rar', '.7z', '.tar', '.gz',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.exe', '.dll', '.bin', '.iso', '.so', '.dylib'
    ],
    "theme": "Light",
    "language": "es"
}

# --- Funciones de Manejo de Configuración ---

def load_config() -> dict:
    """Carga la configuración desde JSON. Si no existe o está corrupto, usa los valores por defecto."""
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
    """Guarda el diccionario de configuración actual en el archivo JSON."""
    try:
        with open(CONFIG_FILE_PATH, 'w', encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error al guardar la configuración: {e}")

def delete_config_file():
    """Elimina el archivo de configuración JSON si existe para restaurar los valores por defecto."""
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            os.remove(CONFIG_FILE_PATH)
    except Exception as e:
        print(f"Error al eliminar el archivo de configuración: {e}")

