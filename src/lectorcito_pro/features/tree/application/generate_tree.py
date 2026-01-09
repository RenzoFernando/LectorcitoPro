from __future__ import annotations

import os

from ....infra.filesystem.report_writer import write_lines
from ....infra.filesystem.tree_builder import iter_tree_lines


def generate_tree_report(
    source_folder: str,
    output_path: str,
    use_config: bool,
    config: dict,
) -> tuple[str, str | None]:
    """Genera un reporte de árbol (misma lógica/formatos que el original)."""
    folder_name = os.path.basename(os.path.normpath(source_folder))
    version = 1
    while True:
        report_filename = f"Arbol_{folder_name}_v{version}.txt"
        final_report_path = os.path.join(output_path, report_filename)
        if not os.path.exists(final_report_path):
            break
        version += 1

    try:
        lines = [f"{folder_name}/\n"]
        lines.extend(iter_tree_lines(source_folder, use_config=use_config, config=config))
        write_lines(final_report_path, lines, encoding="utf-8")
        return "success", final_report_path
    except Exception as e:
        print(f"[Error] No se pudo generar el árbol: {e}")
        return "error", None
