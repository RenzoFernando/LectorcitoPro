import os
import threading
from time import sleep

from core.logger import get_logger
from domain.settings import AppSettings
from services.file_scanner import _get_active_tags, count_files_to_process

logger = get_logger(__name__)


def generate_report(
    source_folder: str,
    output_path: str,
    config: AppSettings | dict,
    progress_callback: callable | None = None,
    cancel_event: threading.Event | None = None
) -> tuple[str, str | None]:
    total_files = count_files_to_process(source_folder, config)
    if total_files == 0:
        return "no_files", None

    important_folders = _get_active_tags(config, "etiquetas_carpetas_importantes")
    text_ext = _get_active_tags(config, "etiquetas_extensiones_incluidas")
    media_ext = set(config.get("media_extensions", []))
    excluded_folders = _get_active_tags(config, "etiquetas_carpetas_excluidas")
    excluded_files = _get_active_tags(config, "etiquetas_archivos_excluidos")

    folder_name = os.path.basename(os.path.normpath(source_folder))
    version = 1
    while True:
        report_filename = f"{folder_name}_v{version}.txt"
        final_report_path = os.path.join(output_path, report_filename)
        if not os.path.exists(final_report_path):
            break
        version += 1

    processed_files = 0
    try:
        with open(final_report_path, "w", encoding="utf-8") as outfile:
            outfile.write("=" * 80 + "\n")
            outfile.write(" LECTORCITO PRO - REPORTE DE PROYECTO\n")
            outfile.write(f" PROYECTO: {folder_name}\n")
            outfile.write(f" RUTA: {source_folder}\n")
            outfile.write("=" * 80 + "\n\n")

            for root, dirs, files in os.walk(source_folder, topdown=True):
                if cancel_event and cancel_event.is_set():
                    break
                dirs[:] = [d for d in dirs if d not in excluded_folders]
                files.sort()

                files_in_dir = []
                for filename in files:
                    if filename in excluded_files:
                        continue
                    is_text = any(filename.lower().endswith(ext) for ext in text_ext)
                    is_media = any(filename.lower().endswith(ext) for ext in media_ext)
                    if is_text or is_media:
                        files_in_dir.append((filename, is_text, is_media))

                if not files_in_dir:
                    continue

                relative_path = os.path.relpath(root, source_folder)
                folder_name_display = relative_path if relative_path != "." else "RAÍZ DEL PROYECTO"
                highlight = " [IMPORTANTE]" if os.path.basename(root) in important_folders else ""
                outfile.write(f"■ CARPETA: {folder_name_display}{highlight}\n")
                outfile.write("└" + ("─" * 78) + "\n\n")

                for filename, is_text, is_media in files_in_dir:
                    if cancel_event and cancel_event.is_set():
                        break

                    current_file_rel_path = os.path.join(folder_name_display, filename)
                    processed_files += 1
                    if progress_callback:
                        progress = (processed_files / total_files) * 100
                        progress_callback(progress, current_file_rel_path)

                    sleep(0.01)

                    file_path = os.path.join(root, filename)
                    outfile.write(f"  ● Archivo: {filename}\n")

                    if is_text:
                        outfile.write("    " + ("-" * 74) + "\n")
                        outfile.write("    >> INICIO DEL CONTENIDO\n\n")
                        try:
                            with open(file_path, "r", encoding="utf-8", errors="ignore") as infile:
                                for line in infile:
                                    outfile.write(f"    {line}")
                        except Exception as e:
                            outfile.write(f"    [Error al leer el archivo: {e}]\n")
                        outfile.write("\n\n    << FIN DEL CONTENIDO\n")
                        outfile.write("    " + ("-" * 74) + "\n\n\n")
                    elif is_media:
                        outfile.write("\n")

                if cancel_event and cancel_event.is_set():
                    break
    except Exception as e:
        logger.error("Error crítico al generar el reporte: %s", e)
        if os.path.exists(final_report_path):
            os.remove(final_report_path)
        return "error", None

    if cancel_event and cancel_event.is_set():
        if os.path.exists(final_report_path):
            os.remove(final_report_path)
        return "cancelled", None

    return "success", final_report_path
