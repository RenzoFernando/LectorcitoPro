from __future__ import annotations

import os


def _get_active_tags(config: dict, tag_key: str) -> set[str]:
    tag_list = config.get(tag_key, [])
    return {tag["nombre"] for tag in tag_list if tag.get("estado") == "activo"}


def _build_tree_recursive(current_path: str, prefix: str, outfile, use_config: bool, config: dict) -> None:
    try:
        elements = sorted(os.listdir(current_path))
    except Exception:
        return

    if use_config:
        excluded_folders = _get_active_tags(config, "etiquetas_carpetas_excluidas")
        excluded_files = _get_active_tags(config, "etiquetas_archivos_excluidos")
        included_extensions = _get_active_tags(config, "etiquetas_extensiones_incluidas")
        media_extensions = set(config.get("media_extensions", []))
        valid_extensions = included_extensions.union(media_extensions)

        filtered_elements: list[str] = []
        for element in elements:
            element_path = os.path.join(current_path, element)
            if os.path.isdir(element_path):
                if element not in excluded_folders:
                    filtered_elements.append(element)
            else:
                if element in excluded_files:
                    continue
                if any(element.lower().endswith(ext) for ext in valid_extensions):
                    filtered_elements.append(element)
        elements = filtered_elements

    pointers = ["├── "] * (len(elements) - 1) + ["└── "]
    for pointer, element in zip(pointers, elements):
        outfile.write(prefix + pointer + element + "\n")
        element_path = os.path.join(current_path, element)
        if os.path.isdir(element_path):
            extension = "│   " if pointer == "├── " else "    "
            _build_tree_recursive(element_path, prefix + extension, outfile, use_config, config)


def generate_tree_report(source_folder: str, output_path: str, use_config: bool, config: dict) -> tuple[str, str | None]:
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
        print(f"[Error] No se pudo generar el árbol: {e}")
        return "error", None
