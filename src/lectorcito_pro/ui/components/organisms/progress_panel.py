"""UI Organism: ProgressPanel.

Encapsula el área central inferior:
- GIF (idle/procesando)
- Barra de progreso (labels + bar)
- Botón Cancelar

La animación GIF y la lógica de progreso se mantienen en `main_window.py`;
este organismo sólo construye y expone los widgets.
"""

from __future__ import annotations

import customtkinter as ctk

from ..molecules.progress_bar import ProgressWidgets


class ProgressPanel(ctk.CTkFrame):
    def __init__(self, parent, *, width: int | None = None, height: int | None = None):
        super().__init__(parent, fg_color="transparent", width=width, height=height)
        if width or height:
            # Mantener geometría estable como en la UI original.
            self.grid_propagate(False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Wrapper para GIF/idle
        self.progress_content_wrapper = ctk.CTkFrame(self, fg_color="transparent")
        self.progress_content_wrapper.grid(row=0, column=0, sticky="nsew", rowspan=4)

        self.lbl_gif_animation = ctk.CTkLabel(self.progress_content_wrapper, text="")
        self.lbl_gif_animation.pack(expand=True)

        # Progreso + labels
        self.widgets = ProgressWidgets.build(self)

        # Botón cancelar (el command se asigna desde el controller)
        self.btn_cancel = ctk.CTkButton(self, width=150, height=28)

    # Atajos para compatibilidad con la ventana principal (acceso directo)
    @property
    def lbl_progress_status(self):
        return self.widgets.lbl_status

    @property
    def lbl_percent(self):
        return self.widgets.lbl_percent

    @property
    def progress_bar(self):
        return self.widgets.bar

    @property
    def lbl_current_file(self):
        return self.widgets.lbl_current_file
