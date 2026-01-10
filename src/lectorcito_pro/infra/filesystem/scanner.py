
from __future__ import annotations


import os
import threading
from dataclasses import dataclass
from typing import Iterator, List, Tuple

from ...features.reports.domain.filters import ReportFilters, filename_matches_any_ext


@dataclass(frozen=True)
class ScannedFile:
    name: str
    is_text: bool
    is_media: bool


def count_files_to_process(source_folder: str, filters: ReportFilters) -> int:
    """Cuenta cuántos archivos serán procesados (texto + media).

    Mantiene el mismo criterio que el original:
    - Excluye carpetas y archivos por nombre completo.
    - Incluye archivos que terminen en extensiones válidas (texto + media).
    """
    file_count = 0
    try:
        for root, dirs, files in os.walk(source_folder, topdown=True):
            # Excluir carpetas (por nombre, no por ruta completa)
            dirs[:] = [d for d in dirs if d not in filters.excluded_folders]

            for filename in files:
                if filename in filters.excluded_files:
                    continue
                if filename_matches_any_ext(filename, filters.all_valid_extensions):
                    file_count += 1
    except OSError:
        return 0

    return file_count


def iter_directories_with_files(
    source_folder: str,
    filters: ReportFilters,
    cancel_event: threading.Event | None = None,
) -> Iterator[tuple[str, list[ScannedFile]]]:
    """Itera directorios que tengan archivos relevantes.

    Devuelve tuplas:
        (root_dir, [ScannedFile, ...])

    El `cancel_event` permite cortar el recorrido sin lanzar excepciones.
    """
    for root, dirs, files in os.walk(source_folder, topdown=True):
        if cancel_event and cancel_event.is_set():
            break

        dirs[:] = [d for d in dirs if d not in filters.excluded_folders]
        files.sort()

        scanned: list[ScannedFile] = []
        for filename in files:
            if cancel_event and cancel_event.is_set():
                break

            if filename in filters.excluded_files:
                continue

            is_text = filename_matches_any_ext(filename, filters.included_extensions)
            is_media = filename_matches_any_ext(filename, filters.media_extensions)

            if is_text or is_media:
                scanned.append(ScannedFile(name=filename, is_text=is_text, is_media=is_media))

        if scanned:
            yield root, scanned
