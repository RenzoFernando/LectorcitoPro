from __future__ import annotations

"""Modelos de dominio para settings.

La aplicación actualmente usa un dict de configuración por compatibilidad.
Estos modelos son opcionales y sirven como referencia/contrato para futuras mejoras.
"""

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
