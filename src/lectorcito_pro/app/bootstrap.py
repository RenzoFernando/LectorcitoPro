from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from .di import build_controller


def main() -> None:
    try:
        controller = build_controller()
        controller.run()
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error Crítico", f"No se pudo iniciar la aplicación:\n\n{e}")
        root.destroy()
