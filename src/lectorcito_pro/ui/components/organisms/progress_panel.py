from __future__ import annotations

import customtkinter as ctk

from ...theme.palette import BTN_W_MAIN, BTN_H_MAIN


class ProgressPanel(ctk.CTkFrame):
    """
    Panel de progreso (sin GIFs).

    Nota: La lógica de mostrar/ocultar widgets la controla `main_window.py` con:
    - toggle_ui_for_processing(...)
    - set_progress(...)
    """

    def __init__(self, parent, width: int, height: int = 135):
        super().__init__(parent, width=width, height=height, corner_radius=10)
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        # Estado / % (fila 0)
        self.lbl_progress_status = ctk.CTkLabel(self, text="", font=("Segoe UI", 11, "bold"))
        self.lbl_percent = ctk.CTkLabel(self, text="0%", font=("Segoe UI", 11, "bold"))

        # Barra (fila 1)
        self.progress_bar = ctk.CTkProgressBar(self, height=10, corner_radius=8, mode="determinate")
        self.progress_bar.set(0)

        # Archivo actual (fila 2)
        self.lbl_current_file = ctk.CTkLabel(self, text="", font=("Segoe UI", 9))

        # Botón cancelar (fila 3, se muestra solo cuando hay procesamiento)
        self.btn_cancel = ctk.CTkButton(
            self,
            text="",
            width=BTN_W_MAIN,
            height=BTN_H_MAIN,
            corner_radius=8,
            font=("Segoe UI", 11, "bold"),
        )

        # Layout base (idle)
        self.lbl_progress_status.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        self.lbl_percent.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="e")
        self.progress_bar.grid(row=1, column=0, padx=10, pady=(5, 5), sticky="ew")
        self.lbl_current_file.grid(row=2, column=0, padx=10, pady=(0, 0), sticky="w")
        # btn_cancel se gridea cuando se activa el procesamiento
