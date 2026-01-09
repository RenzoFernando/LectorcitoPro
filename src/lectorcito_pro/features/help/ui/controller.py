from __future__ import annotations

"""Capa UI (adaptador) para Help.

Actualmente la UI llama directamente al diálogo de infografía, pero este módulo
queda como punto único si luego quieres exponer más ayudas/manuales.
"""

from ..application.open_manual import get_infographic_path, infographic_exists


class HelpUIController:
    def get_manual_path(self) -> str:
        return get_infographic_path()

    def manual_exists(self) -> bool:
        return infographic_exists()
