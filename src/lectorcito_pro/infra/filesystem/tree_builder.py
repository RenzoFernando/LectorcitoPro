from __future__ import annotations

"""Constructor de árbol de directorios (texto).

Este módulo encapsula la lógica de recorrido usada para generar el reporte de árbol.
No cambia el comportamiento: solo mueve el recorrido a infraestructura para reutilizarlo.
"""

import os
from typing import Iterable, Iterator

from ...features.reports.domain.filters import build_filters, filename_matches_any_ext


def iter_tree_lines(
    source_folder: str,
    *,
    use_config: bool,
    config: dict,
) -> Iterator[str]:
    """Genera las líneas del árbol (sin incluir la línea raíz "<folder>/")."""
    filters = build_filters(config) if use_config else None
    yield from _build_tree_recursive(source_folder, prefix="", filters=filters)


def _build_tree_recursive(
    current_path: str,
    prefix: str,
    *,
    filters=None,
) -> Iterator[str]:
    try:
        elements = sorted(os.listdir(current_path))
    except Exception:
        return

    if filters is not None:
        # Filtros (mismo criterio que el original)
        filtered: list[str] = []
        for element in elements:
            element_path = os.path.join(current_path, element)

            if os.path.isdir(element_path):
                if element not in filters.excluded_folders:
                    filtered.append(element)
            else:
                if element in filters.excluded_files:
                    continue
                if filename_matches_any_ext(element, filters.all_valid_extensions):
                    filtered.append(element)
        elements = filtered

    if not elements:
        return

    pointers = ["├── "] * (len(elements) - 1) + ["└── "]
    for pointer, element in zip(pointers, elements):
        yield prefix + pointer + element + "\n"

        element_path = os.path.join(current_path, element)
        if os.path.isdir(element_path):
            extension = "│   " if pointer == "├── " else "    "
            yield from _build_tree_recursive(element_path, prefix + extension, filters=filters)
