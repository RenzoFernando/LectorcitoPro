import os
import threading
from fnmatch import fnmatchcase
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


def _split_gitignore_line(raw_line: str) -> tuple[bool, bool, bool, str, bool] | None:
    line = raw_line.rstrip("\n\r").strip()
    if not line:
        return None
    if line.startswith("\\#") or line.startswith("\\!"):
        line = line[1:]
    elif line.startswith("#"):
        return None

    negate = line.startswith("!")
    if negate:
        line = line[1:]

    line = line.replace("\\", "/").strip()
    if not line:
        return None

    anchored = line.startswith("/")
    if anchored:
        line = line[1:]

    dir_only = line.endswith("/")
    if dir_only:
        line = line[:-1]

    line = line.strip("/")
    if not line:
        return None

    has_slash = "/" in line
    return negate, dir_only, anchored, line, has_slash


def _load_gitignore_rules(source_folder: str, config: dict) -> list[tuple[bool, bool, bool, str, bool]]:
    if not config.get("use_gitignore_exclusions", False):
        return []

    gitignore_path = os.path.join(source_folder, ".gitignore")
    if not os.path.isfile(gitignore_path):
        return []

    rules = []
    try:
        with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as infile:
            for raw_line in infile:
                parsed = _split_gitignore_line(raw_line)
                if parsed is not None:
                    rules.append(parsed)
    except OSError:
        return []

    return rules


def _build_dir_candidates(rel_path: str) -> list[str]:
    normalized_path = rel_path.replace("\\", "/").strip("/")
    if not normalized_path:
        return []

    parts = [part for part in normalized_path.split("/") if part]
    candidates = []
    for index in range(len(parts)):
        candidates.append("/".join(parts[:index + 1]))
    return candidates


def _match_gitignore_path(pattern: str, anchored: bool, has_slash: bool, candidate: str) -> bool:
    candidate = candidate.replace("\\", "/").strip("/")
    if not candidate:
        return False

    if not has_slash:
        return fnmatchcase(candidate.rsplit("/", 1)[-1], pattern)

    if anchored:
        return fnmatchcase(candidate, pattern)

    parts = [part for part in candidate.split("/") if part]
    for index in range(len(parts)):
        suffix = "/".join(parts[index:])
        if fnmatchcase(suffix, pattern):
            return True
    return False


def _is_gitignore_excluded(rel_path: str, is_dir: bool, gitignore_rules: list[tuple[bool, bool, bool, str, bool]]) -> bool:
    if not gitignore_rules:
        return False

    normalized_path = rel_path.replace("\\", "/").strip("/")
    if not normalized_path:
        return False

    dir_candidates = _build_dir_candidates(normalized_path if is_dir else os.path.dirname(normalized_path))
    path_candidates = list(dir_candidates)
    if is_dir:
        if normalized_path not in path_candidates:
            path_candidates.append(normalized_path)
    else:
        path_candidates.append(normalized_path)

    ignored = False
    for negate, dir_only, anchored, pattern, has_slash in gitignore_rules:
        candidates_to_check = dir_candidates if dir_only else path_candidates
        if any(_match_gitignore_path(pattern, anchored, has_slash, candidate) for candidate in candidates_to_check):
            ignored = not negate

    return ignored


def _count_files_to_process(folder: str, config: dict, gitignore_rules: list[tuple[bool, bool, bool, str, bool]]) -> int:
    file_count = 0

    extensions_to_include = _get_active_tags(config, "etiquetas_extensiones_incluidas")
    extensions_to_check = extensions_to_include.union(set(config.get("media_extensions", [])))
    folders_to_exclude = _get_active_tags(config, "etiquetas_carpetas_excluidas")
    files_to_exclude = _get_active_tags(config, "etiquetas_archivos_excluidos")

    try:
        for root, dirs, files in os.walk(folder, topdown=True):
            relative_root = os.path.relpath(root, folder)
            relative_root = "" if relative_root == "." else relative_root
            dirs[:] = [
                d for d in dirs
                if d not in folders_to_exclude and not _is_gitignore_excluded(os.path.join(relative_root, d), True, gitignore_rules)
            ]

            for filename in files:
                if matches_file_rule(filename, files_to_exclude):
                    continue
                if _is_gitignore_excluded(os.path.join(relative_root, filename), False, gitignore_rules):
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
    gitignore_rules = _load_gitignore_rules(source_folder, config)

    total_files = _count_files_to_process(source_folder, config, gitignore_rules)
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
                relative_root = os.path.relpath(root, source_folder)
                relative_root = "" if relative_root == "." else relative_root
                dirs[:] = [
                    d for d in dirs
                    if d not in excluded_folders and not _is_gitignore_excluded(os.path.join(relative_root, d), True, gitignore_rules)
                ]
                files.sort()

                files_in_dir = []
                for filename in files:
                    if matches_file_rule(filename, excluded_files):
                        continue
                    if _is_gitignore_excluded(os.path.join(relative_root, filename), False, gitignore_rules):
                        continue
                    is_text = matches_file_rule(filename, text_ext)
                    is_media = matches_file_rule(filename, media_ext)

                    if is_text or is_media:
                        files_in_dir.append((filename, is_text, is_media))

                if not files_in_dir: continue

                folder_name_display = relative_root if relative_root else _get_tr(config, 'rep_root')
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
    gitignore_rules = _load_gitignore_rules(source_folder, config)

    version = 1
    while True:
        report_filename = f"Arbol_{folder_name}_v{version}.txt"
        final_report_path = os.path.join(output_path, report_filename)
        if not os.path.exists(final_report_path): break
        version += 1

    try:
        with open(final_report_path, "w", encoding="utf-8") as f:
            f.write(f"{folder_name}/\n")
            _build_tree_recursive(source_folder, "", f, config, source_folder, gitignore_rules)
        return "success", final_report_path
    except Exception as e:
        print(f"Error generando arbol: {e}")
        return "error", None


def _build_tree_recursive(current_path, prefix, outfile, config, source_folder, gitignore_rules):
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
        rel_path = os.path.relpath(elem_path, source_folder)
        if os.path.isdir(elem_path):
            if elem not in excluded_folders and not _is_gitignore_excluded(rel_path, True, gitignore_rules):
                filtered_elements.append(elem)
        else:
            if not matches_file_rule(elem, excluded_files) and not _is_gitignore_excluded(rel_path, False, gitignore_rules) and matches_file_rule(elem, valid_ext):
                filtered_elements.append(elem)
    elements = filtered_elements

    pointers = ['├── '] * (len(elements) - 1) + ['└── ']

    for pointer, element in zip(pointers, elements):
        outfile.write(prefix + pointer + element + '\n')
        element_path = os.path.join(current_path, element)
        if os.path.isdir(element_path):
            extension = '│   ' if pointer == '├── ' else '    '
            _build_tree_recursive(element_path, prefix + extension, outfile, config, source_folder, gitignore_rules)