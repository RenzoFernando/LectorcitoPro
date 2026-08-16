import os
import threading
from time import sleep
from i18n.translations import TRANSLATIONS
from model.renderer_factory import get_report_renderer
from model.scanner import ProjectScanner


# =============================================================================
# UTILIDADES DEL PROCESADOR
# =============================================================================

def _get_tr(config: dict, key: str, *args) -> str:
    lang = config.get("language", "es")
    dct = TRANSLATIONS.get(lang, TRANSLATIONS["es"])
    val = dct.get(key, key)
    return val.format(*args)


def _get_raw_tr(config: dict, key: str, fallback: str = "") -> str:
    lang = config.get("language", "es")
    dct = TRANSLATIONS.get(lang, TRANSLATIONS["es"])
    value = dct.get(key, fallback or key)
    if isinstance(value, list):
        value = value[0] if value else fallback or key
    return str(value)


def _get_filename_prefix(config: dict, key: str, fallback: str) -> str:
    value = _get_tr(config, key).strip()
    return value if value and value != key else fallback


def _get_report_labels(config: dict) -> dict[str, str]:
    return {
        "project": _get_raw_tr(config, "rep_project", "PROYECTO: {}"),
        "path": _get_raw_tr(config, "rep_path", "RUTA: {}"),
        "folder": _get_raw_tr(config, "rep_folder", "■ CARPETA: {}"),
        "root": _get_tr(config, "rep_root"),
        "important": _get_raw_tr(config, "rep_important", " [IMPORTANTE]"),
        "file": _get_raw_tr(config, "rep_file", "  ● Archivo: {}"),
        "file_path": _get_raw_tr(config, "rep_file_path", "    Ruta: {}"),
        "content_start": _get_raw_tr(config, "rep_sep_start", "    >> INICIO DEL CONTENIDO: {}"),
        "content_end": _get_raw_tr(config, "rep_sep_end", "    << FIN DEL CONTENIDO: {}"),
        "read_error": _get_raw_tr(config, "rep_read_error", "      [Error al leer el archivo: {}]"),
        "project_label": _get_tr(config, "rep_md_project_label"),
        "path_label": _get_tr(config, "rep_md_path_label"),
        "folder_label": _get_tr(config, "rep_md_folder_label"),
        "file_label": _get_tr(config, "rep_md_file_label"),
        "important_md": _get_tr(config, "rep_md_important"),
        "toc": _get_tr(config, "rep_md_toc"),
        "content_start_md": _get_tr(config, "rep_md_content_start"),
        "content_end_md": _get_tr(config, "rep_md_content_end"),
        "media_notice": _get_tr(config, "rep_md_media_notice"),
        "read_error_md": _get_raw_tr(config, "rep_md_read_error", "Error reading file: {}"),
        "tree_structure": _get_tr(config, "rep_md_tree_structure"),
        "folder_anchor_prefix": _get_tr(config, "rep_md_folder_anchor_prefix"),
        "file_anchor_prefix": _get_tr(config, "rep_md_file_anchor_prefix"),
    }


def _renderer_labels(config: dict, report_extension: str) -> dict[str, str]:
    labels = _get_report_labels(config)
    if report_extension == ".md":
        return {
            "project_label": labels["project_label"],
            "path_label": labels["path_label"],
            "folder_label": labels["folder_label"],
            "file_label": labels["file_label"],
            "root": labels["root"],
            "important": labels["important_md"],
            "toc": labels["toc"],
            "content_start": labels["content_start_md"],
            "content_end": labels["content_end_md"],
            "media_notice": labels["media_notice"],
            "read_error": labels["read_error_md"],
            "tree_structure": labels["tree_structure"],
            "folder_anchor_prefix": labels["folder_anchor_prefix"],
            "file_anchor_prefix": labels["file_anchor_prefix"],
        }
    return {
        "project": labels["project"],
        "path": labels["path"],
        "folder": labels["folder"],
        "root": labels["root"],
        "important": labels["important"],
        "file": labels["file"],
        "file_path": labels["file_path"],
        "content_start": labels["content_start"],
        "content_end": labels["content_end"],
        "read_error": labels["read_error"],
    }


def _next_report_path(
        output_path: str,
        filename_prefix: str,
        project_name: str,
        report_extension: str
) -> str:
    version = 1
    while True:
        report_filename = f"{filename_prefix}_{project_name}_v{version}{report_extension}"
        final_report_path = os.path.join(output_path, report_filename)
        if not os.path.exists(final_report_path):
            return final_report_path
        version += 1


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
    report_extension = config.get("report_extension", ".md")
    if report_extension not in {".md", ".txt"}:
        report_extension = ".md"

    scanner = ProjectScanner(config)
    project = scanner.scan_project(source_folder)
    if project.file_count == 0:
        return "no_files", None

    filename_prefix = _get_filename_prefix(config, "rep_filename_prefix", "Reporte")
    final_report_path = _next_report_path(
        output_path,
        filename_prefix,
        project.name,
        report_extension
    )

    processed_files = 0

    try:
        with open(final_report_path, "w", encoding="utf-8") as outfile:
            renderer = get_report_renderer(
                report_extension,
                outfile,
                _renderer_labels(config, report_extension)
            )
            renderer.write_header(_get_tr(config, "rep_title"), project)
            renderer.write_toc(project)

            for folder in project.folders:
                if cancel_event.is_set():
                    break

                renderer.write_folder(folder)

                for report_file in folder.files:
                    if cancel_event.is_set():
                        break

                    processed_files += 1
                    if progress_callback:
                        progress = (processed_files / project.file_count) * 100
                        progress_callback(progress, report_file.relative_path)

                    sleep(0.01)

                    scanner.read_file(report_file)
                    renderer.write_file(report_file)
                    report_file.content = None
                    report_file.read_error = None

                if cancel_event.is_set():
                    break

    except Exception as error:
        print(f"Error generando reporte: {error}")
        if os.path.exists(final_report_path):
            os.remove(final_report_path)
        return "error", None

    if cancel_event.is_set():
        if os.path.exists(final_report_path):
            os.remove(final_report_path)
        return "cancelled", None

    return "success", final_report_path


# =============================================================================
# GENERACION DE ARBOL
# =============================================================================

def generate_tree_report(
        source_folder: str, output_path: str, config: dict
) -> tuple[str, str | None]:
    source_folder = os.path.abspath(source_folder)
    project_name = os.path.basename(os.path.normpath(source_folder))
    report_extension = config.get("report_extension", ".md")
    if report_extension not in {".md", ".txt"}:
        report_extension = ".md"

    filename_prefix = _get_filename_prefix(config, "rep_tree_filename_prefix", "Arbol")
    final_report_path = _next_report_path(
        output_path,
        filename_prefix,
        project_name,
        report_extension
    )

    try:
        scanner = ProjectScanner(config)
        tree_text = scanner.build_tree_text(source_folder)

        with open(final_report_path, "w", encoding="utf-8") as outfile:
            renderer = get_report_renderer(
                report_extension,
                outfile,
                _renderer_labels(config, report_extension)
            )
            renderer.write_tree(
                _get_tr(config, "rep_md_tree_title"),
                project_name,
                source_folder,
                tree_text
            )
        return "success", final_report_path
    except Exception as error:
        print(f"Error generando arbol: {error}")
        return "error", None
