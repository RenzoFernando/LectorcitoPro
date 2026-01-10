
from __future__ import annotations



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
