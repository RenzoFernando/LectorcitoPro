import os
from dataclasses import dataclass
from typing import Generator, Iterable, List, Set

from core.logger import get_logger
from domain.settings import AppSettings

logger = get_logger(__name__)


@dataclass
class FileEntry:
    root: str
    filename: str
    is_text: bool
    is_media: bool

    @property
    def path(self) -> str:
        return os.path.join(self.root, self.filename)


def _get_active_tags(config: AppSettings | dict, key: str) -> Set[str]:
    tag_list = config.get(key, []) if hasattr(config, "get") else []
    return {tag["nombre"] for tag in tag_list if tag.get("estado") == "activo"}


def count_files_to_process(folder: str, config: AppSettings | dict) -> int:
    file_count = 0

    extensions_to_include = _get_active_tags(config, "etiquetas_extensiones_incluidas")
    extensions_to_check = extensions_to_include.union(set(config.get("media_extensions", [])))
    folders_to_exclude = _get_active_tags(config, "etiquetas_carpetas_excluidas")
    files_to_exclude = _get_active_tags(config, "etiquetas_archivos_excluidos")

    try:
        for root, dirs, files in os.walk(folder, topdown=True):
            dirs[:] = [d for d in dirs if d not in folders_to_exclude]
            for filename in files:
                if filename in files_to_exclude:
                    continue
                if any(filename.lower().endswith(ext) for ext in extensions_to_check):
                    file_count += 1
    except OSError as e:
        logger.error("Error al contar archivos en %s: %s", folder, e)
        return 0
    return file_count


def scan_files(folder: str, config: AppSettings | dict) -> Generator[FileEntry, None, None]:
    text_ext = _get_active_tags(config, "etiquetas_extensiones_incluidas")
    media_ext = set(config.get("media_extensions", []))
    excluded_folders = _get_active_tags(config, "etiquetas_carpetas_excluidas")
    excluded_files = _get_active_tags(config, "etiquetas_archivos_excluidos")

    for root, dirs, files in os.walk(folder, topdown=True):
        dirs[:] = [d for d in dirs if d not in excluded_folders]
        files.sort()
        for filename in files:
            if filename in excluded_files:
                continue
            is_text = any(filename.lower().endswith(ext) for ext in text_ext)
            is_media = any(filename.lower().endswith(ext) for ext in media_ext)
            if is_text or is_media:
                yield FileEntry(root=root, filename=filename, is_text=is_text, is_media=is_media)
