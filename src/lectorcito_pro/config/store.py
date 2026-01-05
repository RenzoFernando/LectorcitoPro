from __future__ import annotations

import copy
import json
import os
from typing import Any, Dict, List

from appdirs import user_config_dir

APP_NAME = "LectorcitoPro"
APP_AUTHOR = "APPS_RenzoFernando"
CFG_NAME = "config.json"

CONFIG_DIR = user_config_dir(APP_NAME, APP_AUTHOR, roaming=True)
os.makedirs(CONFIG_DIR, exist_ok=True)
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR, CFG_NAME)


def _documents_dir() -> str:
    home = os.path.expanduser("~")
    candidates = [
        os.path.join(home, "Documents"),
        os.path.join(home, "OneDrive", "Documents"),
        os.path.join(home, "Documentos"),
        os.path.join(home, "OneDrive", "Documentos"),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return c
    return home


DEFAULT_LECTURAS_PATH = os.path.join(_documents_dir(), "Lecturas")


def to_tags(names: List[str]) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for n in names:
        n = str(n).strip()
        if n:
            out.append({"nombre": n, "estado": "activo"})
    return out


_TAG_KEYS = {
    "etiquetas_carpetas_importantes",
    "etiquetas_extensiones_incluidas",
    "etiquetas_carpetas_excluidas",
    "etiquetas_archivos_excluidos",
}

DEFAULT_CONFIG: Dict[str, Any] = {
    "theme": "Light",
    "language": "es",
    "use_default_path": True,
    "lecturas_path": DEFAULT_LECTURAS_PATH,
    "custom_lecturas_path": DEFAULT_LECTURAS_PATH,
    "etiquetas_carpetas_importantes": to_tags(["src"]),
    "etiquetas_extensiones_incluidas": to_tags(
        [".txt", ".py", ".html", ".java", ".md", ".css", ".js", ".json"]
    ),
    "etiquetas_carpetas_excluidas": to_tags(
        ["__pycache__", "env", "venv", ".venv", ".git", "build", "dist", ".idea"]
    ),
    "etiquetas_archivos_excluidos": to_tags(
        ["Pipfile.lock", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"]
    ),
    "media_extensions": [
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".bmp",
        ".webp",
        ".mp3",
        ".wav",
        ".m4a",
        ".mp4",
        ".avi",
        ".mov",
        ".mkv",
        ".pdf",
    ],
    "last_read_folder": "",
}


def _normalize_tags(value: Any) -> List[Dict[str, str]]:
    if isinstance(value, list) and value:
        if isinstance(value[0], dict):
            out: List[Dict[str, str]] = []
            for item in value:
                nombre = str(item.get("nombre", "")).strip()
                estado = str(item.get("estado", "activo")).strip() or "activo"
                if nombre:
                    out.append({"nombre": nombre, "estado": estado})
            return out
        return to_tags([str(x) for x in value])
    if isinstance(value, list):
        return []
    return []


def load_config() -> Dict[str, Any]:
    cfg: Dict[str, Any] = copy.deepcopy(DEFAULT_CONFIG)

    if os.path.isfile(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f) or {}
            if isinstance(data, dict):
                cfg.update(data)
        except Exception:
            cfg = copy.deepcopy(DEFAULT_CONFIG)

    for k in _TAG_KEYS:
        cfg[k] = _normalize_tags(cfg.get(k, []))

    if cfg.get("use_default_path", True):
        cfg["lecturas_path"] = DEFAULT_LECTURAS_PATH
    else:
        cfg["lecturas_path"] = cfg.get("custom_lecturas_path") or DEFAULT_LECTURAS_PATH

    try:
        os.makedirs(cfg["lecturas_path"], exist_ok=True)
    except Exception:
        pass

    return cfg


def save_config(config: Dict[str, Any]) -> None:
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    cfg.update(config or {})

    for k in _TAG_KEYS:
        cfg[k] = _normalize_tags(cfg.get(k, []))

    if cfg.get("use_default_path", True):
        cfg["lecturas_path"] = DEFAULT_LECTURAS_PATH
    else:
        cfg["custom_lecturas_path"] = cfg.get("custom_lecturas_path") or DEFAULT_LECTURAS_PATH
        cfg["lecturas_path"] = cfg["custom_lecturas_path"]

    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)


def delete_config_file() -> None:
    if os.path.exists(CONFIG_FILE_PATH):
        os.remove(CONFIG_FILE_PATH)
