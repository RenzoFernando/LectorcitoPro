from __future__ import annotations

from typing import Iterable


def write_lines(path: str, lines: Iterable[str], encoding: str = "utf-8") -> None:
    with open(path, "w", encoding=encoding) as f:
        for ln in lines:
            f.write(ln)
