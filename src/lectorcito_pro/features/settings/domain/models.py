
from __future__ import annotations


from dataclasses import dataclass
from typing import Any


@dataclass
class Settings:
    theme: str = "Light"
    language: str = "es"
    use_default_path: bool = True
    lecturas_path: str = ""
    custom_lecturas_path: str = ""
    last_read_folder: str = ""
    raw: dict[str, Any] | None = None
