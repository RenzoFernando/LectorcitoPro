from __future__ import annotations

from typing import Iterable, List, Tuple


def write_lines(file_path: str, lines: Iterable[str], encoding: str = "utf-8") -> None:
    """Escribe líneas en un archivo de texto (una por línea)."""
    with open(file_path, "w", encoding=encoding, newline="\n") as f:
        for line in lines:
            f.write(f"{line}\n")


def write_report(
    output_path: str,
    root_folder: str,
    results: List[Tuple[str, List[str]]],
    encoding: str = "utf-8",
) -> None:
    """Escribe un reporte estructurado por carpetas.

    `results` es una lista de tuplas:
        (nombre_carpeta_relativa, [líneas...])
    """
    header = [
        f"Reporte generado para la carpeta: {root_folder}",
        "=" * 60,
        "",
    ]

    with open(output_path, "w", encoding=encoding, newline="\n") as f:
        for line in header:
            f.write(line + "\n")

        for folder, content_lines in results:
            f.write(f"[CARPETA] {folder}\n")
            f.write("-" * 60 + "\n")
            for line in content_lines:
                f.write(line + "\n")
            f.write("\n")
