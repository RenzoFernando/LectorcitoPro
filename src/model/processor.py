import os
import threading


def _count_files_to_process(folder: str, config: dict) -> int:
    """Cuenta de forma eficiente el número de archivos que se procesarán."""
    file_count = 0
    extensions_to_check = config.get("text_extensions", []) + config.get("media_extensions", [])
    folders_to_exclude = set(config.get("excluded_folders", []))

    try:
        for root, dirs, files in os.walk(folder, topdown=True):
            # Modifica la lista de directorios en el lugar para evitar recorrer las carpetas excluidas.
            dirs[:] = [d for d in dirs if d not in folders_to_exclude]
            for filename in files:
                # Comprueba si la extensión del archivo está en la lista de extensiones a procesar.
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
    Genera un reporte de contenidos de archivos de texto y lista los multimedia.
    Devuelve una tupla (status, path). Status puede ser: 'success', 'cancelled', 'no_files', 'error'.
    """
    total_files = _count_files_to_process(source_folder, config)
    if total_files == 0:
        return "no_files", None

    # Extrae las listas de configuración para un acceso más rápido.
    text_ext = config.get("text_extensions", [])
    media_ext = config.get("media_extensions", [])
    excludes = config.get("excluded_folders", [])

    # Genera un nombre de archivo único para el reporte.
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
            outfile.write(f"REPORTE DE ARCHIVOS EN: {source_folder}\n\n")

            for root, dirs, files in os.walk(source_folder, topdown=True):
                if cancel_event.is_set():
                    break
                dirs[:] = [d for d in dirs if d not in excludes]
                files.sort()

                # Escribe la cabecera de la carpeta solo si contiene archivos relevantes.
                rel_root = os.path.relpath(root, source_folder)
                if rel_root == ".": rel_root = "Carpeta Raíz"

                # Procesa los archivos dentro del directorio actual.
                for filename in files:
                    if cancel_event.is_set():
                        break

                    file_path = os.path.join(root, filename)
                    is_text = any(filename.lower().endswith(ext) for ext in text_ext)
                    is_media = any(filename.lower().endswith(ext) for ext in media_ext)

                    if not (is_text or is_media):
                        continue

                    # Escribe la información del archivo.
                    outfile.write(f"--- Archivo: {os.path.join(rel_root, filename)} ---\n")
                    if is_text:
                        outfile.write("--- CONTENIDO ---\n")
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                                outfile.write(infile.read())
                            outfile.write("\n--- FIN ---\n\n")
                        except Exception as e:
                            outfile.write(f"[Error al leer el archivo: {e}]\n\n")
                    elif is_media:
                        outfile.write("--- ARCHIVO MULTIMEDIA (CONTENIDO NO INCLUIDO) ---\n\n")

                    # Actualiza el progreso.
                    processed_files += 1
                    if progress_callback:
                        progress = (processed_files / total_files) * 100
                        progress_callback(progress)

                if cancel_event.is_set():
                    break

    except Exception as e:
        print(f"Error crítico al generar el reporte: {e}")
        if os.path.exists(final_report_path):
            os.remove(final_report_path)
        return "error", None

    if cancel_event.is_set():
        if os.path.exists(final_report_path):
            os.remove(final_report_path)
        return "cancelled", None

    return "success", final_report_path


def generate_tree_report(
        source_folder: str,
        output_path: str,
        use_config: bool,
        config: dict
) -> tuple[str, str | None]:
    """
    Genera un .txt con la estructura de árbol de un directorio.
    - use_config=True: Aplica los filtros de la configuración.
    - use_config=False: Muestra todos los archivos y carpetas.
    """
    folder_name = os.path.basename(os.path.normpath(source_folder))
    version = 1
    while True:
        report_filename = f"Arbol_{folder_name}_v{version}.txt"
        final_report_path = os.path.join(output_path, report_filename)
        if not os.path.exists(final_report_path):
            break
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
    """Función auxiliar recursiva para construir y escribir la estructura del árbol."""
    try:
        elements = sorted(os.listdir(current_path))
    except OSError:
        return  # No se pudo acceder a la carpeta

    # Filtra los elementos si la opción está activada
    if use_config:
        excluded_folders = set(config.get('excluded_folders', []))
        valid_ext = config.get('text_extensions', []) + config.get('media_extensions', [])

        filtered_elements = []
        for elem in elements:
            elem_path = os.path.join(current_path, elem)
            if os.path.isdir(elem_path):
                if elem not in excluded_folders:
                    filtered_elements.append(elem)
            elif any(elem.lower().endswith(ext) for ext in valid_ext):
                filtered_elements.append(elem)
        elements = filtered_elements

    pointers = ['├── '] * (len(elements) - 1) + ['└── ']
    for pointer, element in zip(pointers, elements):
        outfile.write(prefix + pointer + element + '\n')
        element_path = os.path.join(current_path, element)
        if os.path.isdir(element_path):
            extension = '│   ' if pointer == '├── ' else '    '
            _build_tree_recursive(element_path, prefix + extension, outfile, use_config, config)

