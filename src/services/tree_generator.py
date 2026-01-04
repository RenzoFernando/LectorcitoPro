import os

from domain.settings import AppSettings
from services.file_scanner import _get_active_tags


def generate_tree_report(
    source_folder: str, output_path: str, use_config: bool, config: AppSettings | dict
) -> tuple[str, str | None]:
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
    try:
        elements = sorted(os.listdir(current_path))
    except OSError:
        return

    if use_config:
        excluded_folders = _get_active_tags(config, "etiquetas_carpetas_excluidas")
        excluded_files = _get_active_tags(config, "etiquetas_archivos_excluidos")
        included_ext = _get_active_tags(config, "etiquetas_extensiones_incluidas")
        valid_ext = included_ext.union(set(config.get("media_extensions", [])))

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

    pointers = ["├── "] * (len(elements) - 1) + ["└── "]
    for pointer, element in zip(pointers, elements):
        outfile.write(prefix + pointer + element + "\n")
        element_path = os.path.join(current_path, element)
        if os.path.isdir(element_path):
            extension = "│   " if pointer == "├── " else "    "
            _build_tree_recursive(element_path, prefix + extension, outfile, use_config, config)
