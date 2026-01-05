import os
import threading
from time import sleep


def _get_active_tags(config: dict, key: str) -> set:
    tag_list = config.get(key, [])
    return {tag["nombre"] for tag in tag_list if tag.get("estado") == "activo"}


def _count_files_to_process(folder: str, config: dict) -> int:
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
    except OSError:
        return 0

    return file_count


def generate_report(
    source_folder: str,
    output_path: str,
    config: dict,
    cancel_event: threading.Event,
    progress_callback: callable,
) -> tuple[str, str | None]:
    total_files = _count_files_to_process(source_folder, config)

    if total_files == 0:
        return "no_files", None

    if cancel_event and cancel_event.is_set():
        return "cancelled", None

    os.makedirs(output_path, exist_ok=True)

    important_folders = _get_active_tags(config, "etiquetas_carpetas_importantes")
    included_exts = _get_active_tags(config, "etiquetas_extensiones_incluidas")
    media_exts = set(config.get("media_extensions", []))
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
                    return "cancelled", None

                dirs[:] = [d for d in dirs if d not in excluded_folders]
                files.sort()

                files_in_dir = []
                for filename in files:
                    if filename in excluded_files:
                        continue

                    ext = os.path.splitext(filename)[1].lower()
                    is_media = ext in media_exts
                    is_text = ext in included_exts and not is_media

                    if not (is_text or is_media):
                        continue

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
                        return "cancelled", None

                    current_file_rel_path = os.path.join(folder_name_display, filename)
                    processed_files += 1

                    if progress_callback:
                        progress = (processed_files / total_files) * 100
                        progress_callback(progress, current_file_rel_path)

                    sleep(0.01)

                    file_path = os.path.join(root, filename)
                    outfile.write(f"  ● Archivo: {filename}\n")

                    outfile.write("    " + ("-" * 74) + "\n")
                    outfile.write("    >> INICIO DEL CONTENIDO\n\n")

                    if is_media:
                        outfile.write(f"    [MEDIA] {file_path}\n")
                    elif is_text:
                        try:
                            with open(file_path, "r", encoding="utf-8", errors="ignore") as infile:
                                for line in infile:
                                    outfile.write(f"    {line}")
                        except Exception as e:
                            outfile.write(f"    [Error al leer el archivo: {e}]\n")

                    outfile.write("\n    << FIN DEL CONTENIDO\n\n")

            return "success", final_report_path

    except Exception:
        return "error", None
