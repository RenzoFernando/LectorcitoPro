import os
import threading
from time import sleep


# Extrae los nombres de las etiquetas activas desde la configuración.
def _get_active_tags(config: dict, key: str) -> set:
    tag_list = config.get(key, [])
    return {tag['nombre'] for tag in tag_list if tag.get('estado') == 'activo'}


# Cuenta los archivos a procesar aplicando las reglas de exclusión.
def _count_files_to_process(folder: str, config: dict) -> int:
    file_count = 0

    extensions_to_include = _get_active_tags(config, "etiquetas_extensiones_incluidas")
    extensions_to_check = extensions_to_include.union(set(config.get("media_extensions", [])))
    folders_to_exclude = _get_active_tags(config, "etiquetas_carpetas_excluidas")
    files_to_exclude = _get_active_tags(config, "etiquetas_archivos_excluidos")

    try:
        for root, dirs, files in os.walk(folder, topdown=True):
            # Evita explorar directorios excluidos.
            dirs[:] = [d for d in dirs if d not in folders_to_exclude]

            for filename in files:
                if filename in files_to_exclude:
                    continue
                if any(filename.lower().endswith(ext) for ext in extensions_to_check):
                    file_count += 1
    except OSError as e:
        print(f"Error al contar archivos en {folder}: {e}")
        return 0
    return file_count


# Genera un reporte consolidado de los archivos en un directorio.
def generate_report(
        source_folder: str,
        output_path: str,
        config: dict,
        cancel_event: threading.Event,
        progress_callback: callable
) -> tuple[str, str | None]:
    source_folder = os.path.abspath(source_folder)

    total_files = _count_files_to_process(source_folder, config)
    if total_files == 0:
        return "no_files", None

    # Obtiene las listas de filtros activos desde la configuración.
    important_folders = _get_active_tags(config, "etiquetas_carpetas_importantes")
    text_ext = _get_active_tags(config, "etiquetas_extensiones_incluidas")
    media_ext = set(config.get("media_extensions", []))
    excluded_folders = _get_active_tags(config, "etiquetas_carpetas_excluidas")
    excluded_files = _get_active_tags(config, "etiquetas_archivos_excluidos")

    folder_name = os.path.basename(os.path.normpath(source_folder))
    version = 1
    # Genera un nombre de archivo versionado para no sobrescribir reportes.
    while True:
        report_filename = f"Reporte_{folder_name}_v{version}.txt"
        final_report_path = os.path.join(output_path, report_filename)
        if not os.path.exists(final_report_path): break
        version += 1

    processed_files = 0
    try:
        with open(final_report_path, "w", encoding="utf-8") as outfile:
            # Escribe el encabezado principal del reporte.
            outfile.write("=" * 80 + "\n")
            outfile.write(f" LECTORCITO PRO - REPORTE DE PROYECTO\n")
            outfile.write(f" PROYECTO: {folder_name}\n")
            outfile.write(f" RUTA: {source_folder}\n")
            outfile.write("=" * 80 + "\n\n")

            for root, dirs, files in os.walk(source_folder, topdown=True):
                if cancel_event.is_set(): break
                dirs[:] = [d for d in dirs if d not in excluded_folders]
                files.sort()

                # Filtra los archivos del directorio actual según la configuración.
                files_in_dir = []
                for filename in files:
                    if filename in excluded_files: continue
                    is_text = any(filename.lower().endswith(ext) for ext in text_ext)
                    is_media = any(filename.lower().endswith(ext) for ext in media_ext)
                    if is_text or is_media:
                        files_in_dir.append((filename, is_text, is_media))

                if not files_in_dir: continue

                # Escribe la cabecera para la carpeta actual.
                relative_path = os.path.relpath(root, source_folder)
                folder_name_display = relative_path if relative_path != '.' else 'RAÍZ DEL PROYECTO'
                highlight = " [IMPORTANTE]" if os.path.basename(root) in important_folders else ""
                outfile.write(f"■ CARPETA: {folder_name_display}{highlight}\n")
                outfile.write(f"└" + ("─" * 78) + "\n\n")

                for filename, is_text, is_media in files_in_dir:
                    if cancel_event.is_set(): break

                    # Actualiza el progreso y notifica a la vista.
                    current_file_rel_path = os.path.join(folder_name_display, filename)
                    processed_files += 1
                    if progress_callback:
                        progress = (processed_files / total_files) * 100
                        progress_callback(progress, current_file_rel_path)

                    sleep(0.01)

                    file_path = os.path.join(root, filename)

                    rel_path_from_root = os.path.relpath(file_path, source_folder)

                    outfile.write(f"  ● Archivo: {filename}\n")
                    outfile.write(f"    Ruta: {rel_path_from_root}\n")

                    # Escribe el contenido del archivo si es de texto.
                    if is_text:
                        outfile.write("    " + ("-" * 74) + "\n")
                        outfile.write(f"    >> INICIO DEL CONTENIDO: {filename}\n\n")

                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                                for line in infile:
                                    outfile.write(f"    {line}")
                        except Exception as e:
                            outfile.write(f"    [Error al leer el archivo: {e}]\n")

                        outfile.write(f"\n\n    << FIN DEL CONTENIDO: {filename}\n")
                        outfile.write("    " + ("-" * 74) + "\n\n\n")
                    # Si es multimedia, solo deja un espacio.
                    elif is_media:
                        outfile.write("\n")

                if cancel_event.is_set(): break
    except Exception as e:
        print(f"Error crítico al generar el reporte: {e}")
        if os.path.exists(final_report_path): os.remove(final_report_path)
        return "error", None

    # Si se canceló el proceso, elimina el archivo incompleto.
    if cancel_event.is_set():
        if os.path.exists(final_report_path): os.remove(final_report_path)
        return "cancelled", None

    return "success", final_report_path

# Genera un reporte en forma de árbol de directorios.
def generate_tree_report(
        source_folder: str, output_path: str, config: dict
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
            _build_tree_recursive(source_folder, "", f, config)
        return "success", final_report_path
    except Exception as e:
        print(f"Error al generar el árbol de directorios: {e}")
        return "error", None

# Construye recursivamente el árbol de directorios aplicando los filtros.
def _build_tree_recursive(current_path, prefix, outfile, config):
    try:
        elements = sorted(os.listdir(current_path))
    except OSError:
        return

    # Siempre usa la configuración para filtrar
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

    # Dibuja los conectores del árbol y llama recursivamente para los directorios.
    pointers = ['├── '] * (len(elements) - 1) + ['└── ']
    for pointer, element in zip(pointers, elements):
        outfile.write(prefix + pointer + element + '\n')
        element_path = os.path.join(current_path, element)
        if os.path.isdir(element_path):
            extension = '│   ' if pointer == '├── ' else '    '
            _build_tree_recursive(element_path, prefix + extension, outfile, config)