import os
import threading
from time import sleep
from file_rules import matches_file_rule
from view.translations import TRANSLATIONS


# =============================================================================
# UTILIDADES DEL PROCESADOR
# =============================================================================

def _get_active_tags(config: dict, key: str) -> set:
    tag_list = config.get(key, [])
    return {tag['nombre'] for tag in tag_list if tag.get('estado') == 'activo'}


def _get_tr(config: dict, key: str, *args) -> str:
    lang = config.get("language", "es")
    dct = TRANSLATIONS.get(lang, TRANSLATIONS["es"])
    val = dct.get(key, key)
    return val.format(*args)


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
                if matches_file_rule(filename, files_to_exclude):
                    continue
                if matches_file_rule(filename, extensions_to_check):
                    file_count += 1
    except OSError as e:
        print(f"Error contando archivos: {e}")
        return 0
    return file_count


# =============================================================================
# GENERACION DE REPORTE COMPLETO
# =============================================================================

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

    important_folders = _get_active_tags(config, "etiquetas_carpetas_importantes")
    text_ext = _get_active_tags(config, "etiquetas_extensiones_incluidas")
    media_ext = set(config.get("media_extensions", []))
    excluded_folders = _get_active_tags(config, "etiquetas_carpetas_excluidas")
    excluded_files = _get_active_tags(config, "etiquetas_archivos_excluidos")

    report_ext = config.get("report_extension", ".txt")
    folder_name = os.path.basename(os.path.normpath(source_folder))

    version = 1
    while True:
        report_filename = f"Reporte_{folder_name}_v{version}{report_ext}"
        final_report_path = os.path.join(output_path, report_filename)
        if not os.path.exists(final_report_path): break
        version += 1

    processed_files = 0

    try:
        with open(final_report_path, "w", encoding="utf-8") as outfile:
            outfile.write("=" * 80 + "\n")
            outfile.write(f" {_get_tr(config, 'rep_title')}\n")
            outfile.write(f" {_get_tr(config, 'rep_project', folder_name)}\n")
            outfile.write(f" {_get_tr(config, 'rep_path', source_folder)}\n")
            outfile.write("=" * 80 + "\n\n")

            for root, dirs, files in os.walk(source_folder, topdown=True):
                if cancel_event.is_set(): break
                dirs[:] = [d for d in dirs if d not in excluded_folders]
                files.sort()

                files_in_dir = []
                for filename in files:
                    if matches_file_rule(filename, excluded_files):
                        continue
                    is_text = matches_file_rule(filename, text_ext)
                    is_media = matches_file_rule(filename, media_ext)

                    if is_text or is_media:
                        files_in_dir.append((filename, is_text, is_media))

                if not files_in_dir: continue

                relative_path = os.path.relpath(root, source_folder)
                folder_name_display = relative_path if relative_path != '.' else _get_tr(config, 'rep_root')
                highlight = _get_tr(config, 'rep_important') if os.path.basename(root) in important_folders else ""

                outfile.write(f"{_get_tr(config, 'rep_folder', folder_name_display)}{highlight}\n")
                outfile.write(f"└" + ("─" * 78) + "\n\n")

                for filename, is_text, is_media in files_in_dir:
                    if cancel_event.is_set(): break

                    current_file_rel_path = os.path.join(folder_name_display, filename)
                    processed_files += 1
                    if progress_callback:
                        progress = (processed_files / total_files) * 100
                        progress_callback(progress, current_file_rel_path)

                    sleep(0.01)

                    file_path = os.path.join(root, filename)
                    rel_path_from_root = os.path.relpath(file_path, source_folder)

                    outfile.write(f"{_get_tr(config, 'rep_file', filename)}\n")
                    outfile.write(f"{_get_tr(config, 'rep_file_path', rel_path_from_root)}\n")

                    if is_text:
                        outfile.write("    " + ("-" * 74) + "\n")
                        outfile.write(f"{_get_tr(config, 'rep_sep_start', filename)}\n\n")

                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                                for line in infile:
                                    outfile.write(f"    {line}")
                        except Exception as e:
                            outfile.write(f"{_get_tr(config, 'rep_read_error', str(e))}\n")

                        outfile.write(f"\n\n{_get_tr(config, 'rep_sep_end', filename)}\n")
                        outfile.write("    " + ("-" * 74) + "\n\n\n")

                    elif is_media:
                        outfile.write("\n")

                if cancel_event.is_set(): break

    except Exception as e:
        print(f"Error generando reporte: {e}")
        if os.path.exists(final_report_path): os.remove(final_report_path)
        return "error", None

    if cancel_event.is_set():
        if os.path.exists(final_report_path): os.remove(final_report_path)
        return "cancelled", None

    return "success", final_report_path


# =============================================================================
# GENERACION DE ARBOL
# =============================================================================

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
        print(f"Error generando arbol: {e}")
        return "error", None


def _build_tree_recursive(current_path, prefix, outfile, config):
    try:
        elements = sorted(os.listdir(current_path))
    except OSError:
        return

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
            if not matches_file_rule(elem, excluded_files) and matches_file_rule(elem, valid_ext):
                filtered_elements.append(elem)
    elements = filtered_elements

    pointers = ['├── '] * (len(elements) - 1) + ['└── ']

    for pointer, element in zip(pointers, elements):
        outfile.write(prefix + pointer + element + '\n')
        element_path = os.path.join(current_path, element)
        if os.path.isdir(element_path):
            extension = '│   ' if pointer == '├── ' else '    '
            _build_tree_recursive(element_path, prefix + extension, outfile, config)
