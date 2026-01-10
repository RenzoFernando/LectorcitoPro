from __future__ import annotations

from tkinter import filedialog
from typing import Optional, Any

# Se añade parent: Any = None para aceptar la ventana de CTk
def ask_directory(title: str = "", initial_dir: str | None = None, parent: Any = None) -> str:
    """Abre un selector de carpetas del sistema de forma segura."""
    try:
        # Intentamos abrir el diálogo
        return filedialog.askdirectory(title=title, initialdir=initial_dir, parent=parent) or ""
    except Exception:
        # Si Tcl/Tkinter falla (app destruida o referencia perdida),
        # retornamos cadena vacía para cancelar la operación suavemente.
        return ""