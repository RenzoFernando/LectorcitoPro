from __future__ import annotations

import os
from typing import Callable, Optional, Tuple

from ....core.errors import ProcessingCancelled
from ....infra.filesystem.file_reader import describe_media_file, read_text_file
from ....infra.filesystem.report_writer import write_report
from ....infra.filesystem.scanner import count_files_to_process, iter_directories_with_files
from ..domain.filters import build_filters


ProgressCallback = Callable[[float, str], None]


def generate_report(
    *,
    source_folder: str,
    output_path: str,
    config: dict,
    cancel_event=None,
    progress_callback: Optional[ProgressCallback] = None,
) -> Tuple[str, Optional[str]]:
    """Genera un reporte de lectura para `source_folder`.

    Retorna:
        ("success", report_path) si todo salió bien.
        ("no_files", None) si no se encontró nada que reportar.
        ("cancelled", None) si el usuario canceló.
        ("error", None) ante cualquier error inesperado.

    Nota:
    - Mantiene la lógica de negocio actual: usa `config` (tags activos) para construir filtros.
    - Reusa el scanner del proyecto (count_files_to_process / iter_directories_with_files).
    """
    try:
        if cancel_event is not None and cancel_event.is_set():
            raise ProcessingCancelled("Operación cancelada antes de iniciar.")

        filters = build_filters(config or {})
        os.makedirs(output_path, exist_ok=True)

        folder_name = os.path.basename(os.path.normpath(source_folder)) or "Lectura"
        version = 1
        while True:
            report_filename = f"Reporte_{folder_name}_v{version}.txt"
            report_path = os.path.join(output_path, report_filename)
            if not os.path.exists(report_path):
                break
            version += 1

        total_files = count_files_to_process(source_folder, filters)
        if total_files <= 0:
            return "no_files", None

        processed = 0
        results: list[tuple[str, list[str]]] = []

        for rel_root, scanned_files in iter_directories_with_files(
            source_folder, filters, cancel_event=cancel_event
        ):
            if cancel_event is not None and cancel_event.is_set():
                raise ProcessingCancelled("Operación cancelada durante el proceso.")

            abs_root = source_folder if rel_root == "." else os.path.join(source_folder, rel_root)
            folder_lines: list[str] = []

            for sf in scanned_files:
                if cancel_event is not None and cancel_event.is_set():
                    raise ProcessingCancelled("Operación cancelada durante la lectura.")

                file_path = os.path.join(abs_root, sf.name)
                rel_file_path = os.path.relpath(file_path, source_folder)

                folder_lines.append(f"[ARCHIVO] {rel_file_path}")
                folder_lines.append("-" * 60)

                if sf.is_media:
                    folder_lines.append(describe_media_file(file_path))
                else:
                    content, error = read_text_file(file_path)
                    if error:
                        folder_lines.append(f"[ERROR] {error}")
                    else:
                        folder_lines.extend(content.splitlines() if content.strip() else ["(archivo vacío)"])

                folder_lines.append("")

                processed += 1
                if progress_callback:
                    try:
                        progress = (processed / total_files) * 100.0
                        progress_callback(progress, rel_file_path)
                    except Exception:
                        pass

            results.append((folder_name if rel_root == "." else rel_root, folder_lines))

        write_report(report_path, source_folder, results)
        return "success", report_path

    except ProcessingCancelled:
        return "cancelled", None
    except Exception as e:
        print(f"[Error] No se pudo generar el reporte: {e}")
        return "error", None
