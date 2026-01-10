from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from ..core.logging import configure_logging
from .di import build_controller


def main() -> None:
    # Hook central para configurar logging (sin afectar la lógica de negocio).
    configure_logging()

    try:
        controller = build_controller()
        controller.run()
    except Exception as e:
        # Fallback: mostrar error crítico sin depender de la ventana principal.
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error Crítico", f"No se pudo iniciar la aplicación:\n\n{e}")
        root.destroy()
