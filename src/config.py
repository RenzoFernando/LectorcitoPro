import os
import json
from appdirs import user_config_dir
import tkinter.messagebox as mb

# --- Constantes de Configuración ---
APP_NAME = "LectorcitoPro"
APP_AUTHOR = "RenzoFernando"
CFG_NAME = "config.json"

# --- Ruta del Archivo de Configuración ---
# Usa una carpeta estándar del sistema operativo para guardar la configuración.
_config_dir = user_config_dir(APP_NAME, APP_AUTHOR, roaming=True)
os.makedirs(_config_dir, exist_ok=True)
CONFIG_FILE_PATH = os.path.join(_config_dir, CFG_NAME)

# --- Configuración por Defecto ---
DEFAULT_CONFIG = {
    "lecturas_path": "",
    "last_read_folder": "",
    "text_extensions": [".txt", ".py", ".html", ".java", ".md", ".css", ".js", ".json", ".xml", ".yml"],
    "excluded_folders": ["__pycache__", "venv", ".venv", "node_modules", ".git", "build", "dist", ".idea"],
    "theme": "Light",
    "language": "es"
}

# --- Funciones de Manejo ---
def load_config() -> dict:
    if os.path.exists(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, 'r', encoding="utf-8") as f:
                data = json.load(f)
            for key, value in DEFAULT_CONFIG.items():
                data.setdefault(key, value)
            return data
        except (json.JSONDecodeError, TypeError):
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config: dict):
    try:
        with open(CONFIG_FILE_PATH, 'w', encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        mb.showerror("Error", f"No se pudo guardar la configuración:\n{e}")

load_cfg = load_config
save_cfg = save_config