import os
import threading
from time import sleep


def _get_active_tags(config: dict, key: str) -> set:
    """Extrae los nombres de las etiquetas activas de una lista de configuración."""
    tag_list = config.get(key, [])
    return {tag['nombre'] for tag in tag_list if tag.get('estado') == 'activo'}


def _count_files_to_process(folder: str, config: dict) -> int:
    """Cuenta de forma eficiente el número de archivos que se procesarán, respetando las exclusiones."""
    file_count = 0

    # Extraer nombres de las etiquetas activas
    extensions_to_include = _get_active_tags(config, "etiquetas_extensiones_incluidas")
    extensions_to_check = extensions_to_include.union(set(config.get("media_extensions", [])))
    folders_to_exclude = _get_active_tags(config, "etiquetas_carpetas_excluidas")
    files_to_exclude = _get_active_tags(config, "etiquetas_archivos_excluidos")

    try:
        for root, dirs, files in os.walk(folder, topdown=True):
            # Filtrar directorios para no explorarlos
            dirs[:] = [d for d in dirs if d not in folders_to_exclude]
            for filename in files:
                if filename in files_to_exclude:
                    continue
                # Comprobar si alguna extensión coincide
                if any(filename.lower().endswith(ext) for ext in extensions_to_check):
                    file_count += 1
    except OSError as e:
        print(f"Error al contar archivos en {folder}: {e}")
        return 0
    return file_count


def generate_report(
        source_folder: str,
        output_path: str,
        config: dict,
        cancel_event: threading.Event,
        progress_callback: callable
) -> tuple[str, str | None]:
    """
    Genera un reporte de contenidos de archivos, respetando la nueva lógica de Ver/No Ver.
    Devuelve una tupla (status, path). Status: 'success', 'cancelled', 'no_files', 'error'.
    """
    total_files = _count_files_to_process(source_folder, config)
    if total_files == 0:
        return "no_files", None

    # Obtener listas de etiquetas activas para el procesamiento
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
        if not os.path.exists(final_report_path): break
        version += 1

    processed_files = 0
    try:
        with open(final_report_path, "w", encoding="utf-8") as outfile:
            outfile.write(f"REPORTE DE ARCHIVOS EN: {source_folder}\n\n")

            for root, dirs, files in os.walk(source_folder, topdown=True):
                if cancel_event.is_set(): break
                dirs[:] = [d for d in dirs if d not in excluded_folders]
                files.sort()

                files_in_dir = []
                for filename in files:
                    if filename in excluded_files: continue
                    is_text = any(filename.lower().endswith(ext) for ext in text_ext)
                    is_media = any(filename.lower().endswith(ext) for ext in media_ext)
                    if is_text or is_media:
                        files_in_dir.append((filename, is_text, is_media))

                if not files_in_dir: continue

                relative_path = os.path.relpath(root, source_folder)
                folder_name_display = relative_path if relative_path != '.' else '.'
                highlight = " (CARPETA IMPORTANTE)" if os.path.basename(root) in important_folders else ""
                outfile.write(f"Carpeta: {folder_name_display}{highlight}\n")

                for filename, is_text, is_media in files_in_dir:
                    if cancel_event.is_set(): break

                    current_file_rel_path = os.path.join(folder_name_display, filename)
                    processed_files += 1
                    if progress_callback:
                        progress = (processed_files / total_files) * 100
                        progress_callback(progress, current_file_rel_path)

                    sleep(0.01)

                    file_path = os.path.join(root, filename)
                    outfile.write(f"    Archivo: {filename}\n")
                    outfile.write(f"    -------- CONTENIDO --------\n")

                    if is_text:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                                for line in infile:
                                    outfile.write(f"    {line}")
                        except Exception as e:
                            outfile.write(f"    [Error al leer el archivo: {e}]\n")
                    elif is_media:
                        outfile.write("    (Archivo multimedia, contenido no incluido)\n")

                    outfile.write(f"\n    -------- FIN --------\n\n")

                if cancel_event.is_set(): break
    except Exception as e:
        print(f"Error crítico al generar el reporte: {e}")
        if os.path.exists(final_report_path): os.remove(final_report_path)
        return "error", None

    if cancel_event.is_set():
        if os.path.exists(final_report_path): os.remove(final_report_path)
        return "cancelled", None

    return "success", final_report_path


def generate_tree_report(
        source_folder: str, output_path: str, use_config: bool, config: dict
) -> tuple[str, str | None]:
    folder_name = os.path.basename(os.path.normpath(source_folder))
    version = 1
    while True:
        report_filename = f"Arbol_{folder_name}_v{version}.txt"
        final_report_path = os.path.join(output_path, report_filename)
        if not os.path.exists(final_report_path): break
        version += 1

    try:
        with open(final_report_path, "w", encoding="utf-8") as f:
            f.write(f"{folder_name}/\n")
            _build_tree_recursive(source_folder, "", f, use_config, config)
        return "success", final_report_path
    except Exception as e:
        print(f"Error al generar el árbol de directorios: {e}")
        return "error", None


def _build_tree_recursive(current_path, prefix, outfile, use_config, config):
    try:
        elements = sorted(os.listdir(current_path))
    except OSError:
        return

    if use_config:
        excluded_folders = _get_active_tags(config, "etiquetas_carpetas_excluidas")
        excluded_files = _get_active_tags(config, "etiquetas_archivos_excluidos")
        included_ext = _get_active_tags(config, "etiquetas_extensiones_incluidas")
        valid_ext = included_ext.union(set(config.get('media_extensions', [])))

        filtered_elements = []
        for elem in elements:
            elem_path = os.path.join(current_path, elem)
            if os.path.isdir(elem_path):
                if elem not in excluded_folders:
                    filtered_elements.append(elem)
            else:
                if elem not in excluded_files and any(elem.lower().endswith(ext) for ext in valid_ext):
                    filtered_elements.append(elem)
        elements = filtered_elements

    pointers = ['├── '] * (len(elements) - 1) + ['└── ']
    for pointer, element in zip(pointers, elements):
        outfile.write(prefix + pointer + element + '\n')
        element_path = os.path.join(current_path, element)
        if os.path.isdir(element_path):
            extension = '│   ' if pointer == '├── ' else '    '
            _build_tree_recursive(element_path, prefix + extension, outfile, use_config, config)
