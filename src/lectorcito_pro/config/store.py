from __future__ import annotations

import json
import os
from appdirs import user_config_dir

# --- Constantes de la Aplicación ---
APP_NAME = "LectorcitoPro"
APP_AUTHOR = "APPS_RenzoFernando"
CFG_NAME = "config.json"

# --- Rutas de Configuración ---
CONFIG_DIR = user_config_dir(APP_NAME, APP_AUTHOR, roaming=True)
os.makedirs(CONFIG_DIR, exist_ok=True)
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR, CFG_NAME)

# Ruta por defecto para guardar reportes (MISMO COMPORTAMIENTO QUE EL CÓDIGO ORIGINAL)
DEFAULT_LECTURAS_PATH = os.path.join(CONFIG_DIR, "Lecturas")
os.makedirs(DEFAULT_LECTURAS_PATH, exist_ok=True)


def to_tags(items: list[str]) -> list[dict]:
    """Convierte una lista de strings a lista de dicts con estado 'activo'."""
    return [{"nombre": item, "estado": "activo"} for item in items]


# --- Configuración por Defecto (copiada del código original) ---
DEFAULT_CONFIG = {
    "use_default_path": True,
    "custom_lecturas_path": "",
    "lecturas_path": DEFAULT_LECTURAS_PATH,
    "last_read_folder": "",
    "theme": "Light",
    "language": "es",
    "etiquetas_carpetas_importantes": to_tags(
        ["src"]
    ),
    "etiquetas_extensiones_incluidas": to_tags(
        [".txt", ".py", ".html", ".java", ".md", ".css", ".js", ".json"]
    ),
    "etiquetas_carpetas_excluidas": to_tags(
        ["__pycache__", "env", "venv", ".venv", ".git", "build", "dist", ".idea"]
    ),
    "etiquetas_archivos_excluidos": to_tags(
        ["Pipfile.lock", "package.json", "package-lock.json"]
    ),
    "media_extensions": [
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp", ".svg", ".ico",
        ".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm",
        ".mp3", ".wav", ".aac", ".flac", ".ogg", ".wma", ".m4a",
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        ".exe", ".dll", ".so", ".dylib", ".app",
        ".bin", ".iso", ".img", ".dmg",
        ".class", ".jar", ".war", ".ear",
        ".pyc", ".pyo", ".pyd",
        ".o", ".obj", ".a", ".lib",
        ".ttf", ".otf", ".woff", ".woff2",
        ".psd", ".ai", ".eps",
        ".bak", ".tmp", ".log", ".dat",
        ".cer", ".crt", ".pem", ".key", ".pfx"
    ]
}


def _migrate_config(config_data: dict) -> dict:
    """Migra configuraciones viejas a la estructura actual (compatibilidad)."""
    def convert_tags(key: str):
        if key in config_data and isinstance(config_data[key], list):
            config_data[key] = to_tags(config_data[key])

    convert_tags("etiquetas_carpetas_importantes")
    convert_tags("etiquetas_extensiones_incluidas")
    convert_tags("etiquetas_carpetas_excluidas")
    convert_tags("etiquetas_archivos_excluidos")
    return config_data


def load_config() -> dict:
    """Carga la configuración desde disco y hace merge con DEFAULT_CONFIG."""
    if os.path.exists(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            config_data = _migrate_config(config_data)

            config_completa = DEFAULT_CONFIG.copy()
            config_completa.update(config_data)
            return config_completa

        except json.JSONDecodeError:
            return DEFAULT_CONFIG.copy()
        except Exception:
            return DEFAULT_CONFIG.copy()

    return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> None:
    """Guarda la configuración a disco."""
    try:
        config_to_save = DEFAULT_CONFIG.copy()
        config_to_save.update(config or {})

        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(config_to_save, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"[Error] No se pudo guardar la configuración: {e}")


def delete_config_file() -> None:
    """Elimina el archivo de configuración si existe."""
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            os.remove(CONFIG_FILE_PATH)
    except Exception as e:
        print(f"[Error] No se pudo eliminar el archivo de configuración: {e}")
