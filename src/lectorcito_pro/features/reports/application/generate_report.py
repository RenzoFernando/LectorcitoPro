from __future__ import annotations

import os
import threading
from time import sleep

from ....infra.filesystem.file_reader import read_text_file
from ....infra.filesystem.scanner import count_files_to_process, iter_directories_with_files
from ..domain.filters import build_filters


def generate_report(
    source_folder: str,
    output_path: str,
    config: dict,
    cancel_event: threading.Event | None = None,
    progress_callback=None,
) -> tuple[str, str | None]:
    """Genera el reporte consolidado del proyecto.

    ✅ Mantiene el mismo comportamiento y formato del reporte original.
    - Recorre el proyecto recursivamente.
    - Aplica filtros configurables.
    - Incluye archivos de texto con su contenido.
    - Lista archivos multimedia (sin incluir contenido).
    - Soporta cancelación y progreso.
    """
    filters = build_filters(config)

    total_files = count_files_to_process(source_folder, filters)
    if total_files == 0:
        return "no_files", None

    if cancel_event and cancel_event.is_set():
        return "cancelled", None

    os.makedirs(output_path, exist_ok=True)

    folder_name = os.path.basename(os.path.normpath(source_folder))
    version = 1
    while True:
        report_filename = f"Reporte_{folder_name}_v{version}.txt"
        final_report_path = os.path.join(output_path, report_filename)
        if not os.path.exists(final_report_path):
            break
        version += 1

    processed_files = 0

    try:
        with open(final_report_path, "w", encoding="utf-8") as outfile:
            # Encabezado (mismo formato del viejo/original)
            outfile.write("=" * 80 + "\n")
            outfile.write(" LECTORCITO PRO - REPORTE DE PROYECTO\n")
            outfile.write(f" PROYECTO: {folder_name}\n")
            outfile.write(f" RUTA: {source_folder}\n")
            outfile.write("=" * 80 + "\n\n")

            for root, scanned_files in iter_directories_with_files(source_folder, filters, cancel_event=cancel_event):
                if cancel_event and cancel_event.is_set():
                    break

                relative_path = os.path.relpath(root, source_folder)
                folder_name_display = relative_path if relative_path != "." else "RAÍZ DEL PROYECTO"
                highlight = " [IMPORTANTE]" if os.path.basename(root) in filters.important_folders else ""

                outfile.write(f"■ CARPETA: {folder_name_display}{highlight}\n")
                outfile.write("└" + ("─" * 78) + "\n\n")

                for item in scanned_files:
                    if cancel_event and cancel_event.is_set():
                        break

                    processed_files += 1
                    progress = (processed_files / total_files) * 100

                    if progress_callback:
                        progress_callback(progress, item.name)

                    sleep(0.01)

                    file_path = os.path.join(root, item.name)
                    outfile.write(f"  ● Archivo: {item.name}\n")

                    if item.is_text:
                        outfile.write("    " + ("-" * 74) + "\n")
                        outfile.write("    >> INICIO DEL CONTENIDO\n\n")
                        try:
                            content = read_text_file(file_path, encoding="utf-8")
                            for line in content.splitlines(True):
                                outfile.write(f"    {line}")
                        except Exception as e:
                            outfile.write(f"    [Error al leer el archivo: {e}]\n")

                        # Igual al original: 2 saltos de línea antes del cierre + separador final
                        outfile.write("\n\n    << FIN DEL CONTENIDO\n")
                        outfile.write("    " + ("-" * 74) + "\n\n")

                    elif item.is_media:
                        # Igual al original: no imprime contenido adicional
                        outfile.write("\n")

    except Exception as e:
        print(f"[Error] Se produjo una excepción al escribir el reporte: {e}")
        try:
            if os.path.exists(final_report_path):
                os.remove(final_report_path)
        except Exception:
            pass
        return "error", None

    # En el original GUI, al cancelar se elimina el reporte parcial.
    if cancel_event and cancel_event.is_set():
        try:
            if os.path.exists(final_report_path):
                os.remove(final_report_path)
        except Exception:
            pass
        return "cancelled", None

    return "success", final_report_path
