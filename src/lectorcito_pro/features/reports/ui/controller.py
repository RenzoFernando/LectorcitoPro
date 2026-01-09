from __future__ import annotations

"""Capa UI (adaptador) para la funcionalidad de reportes.

Actualmente, la UI real está implementada en `ui/app_window/bindings.py`.
Este módulo existe para mantener la estructura por features y permitir
que la UI consuma un controlador específico de reportes si se desea.

No cambia lógica: solo delega al caso de uso `generate_report`.
"""

import threading
from typing import Callable, Optional

from ..application.generate_report import generate_report


class ReportsUIController:
    def generate(
        self,
        *,
        source_folder: str,
        output_path: str,
        config: dict,
        cancel_event: threading.Event | None = None,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> tuple[str, str | None]:
        return generate_report(
            source_folder=source_folder,
            output_path=output_path,
            config=config,
            cancel_event=cancel_event,
            progress_callback=progress_callback,
        )
