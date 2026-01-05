from __future__ import annotations

import sys
from pathlib import Path


def _find_project_root_with_recursos(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "recursos").is_dir():
            return parent
    return start.parents[3]


def resource_path(relative_path: str) -> str:
    try:
        base_path = Path(sys._MEIPASS)
        return str(base_path / "recursos" / relative_path)
    except Exception:
        here = Path(__file__).resolve()
        root = _find_project_root_with_recursos(here)
        return str(root / "recursos" / relative_path)
