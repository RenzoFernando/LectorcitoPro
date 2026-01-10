"""UI Page: HomePage.

La página principal (contenido central) de la aplicación.
Contiene:
- Header (logo + saludo)
- Botones principales
- Panel de progreso (GIF + barra + cancelar)

La ventana principal (`main_window.py`) se encarga del layout general y de la lógica.
"""

from __future__ import annotations

import customtkinter as ctk

from ..atoms.buttons import colored_main_button, main_button
from ..organisms.header import Header
from ..organisms.progress_panel import ProgressPanel
from ...theme.palette import COLORS, PROGRESS_W


class HomePage(ctk.CTkFrame):
    def __init__(self, parent, *, logo_image=None):
        super().__init__(parent, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header = Header(self, logo_image=logo_image)
        self.header.grid(row=0, column=0, pady=(0, 10), sticky="n")

        # Botones principales
        self.main_buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_buttons_frame.grid(row=1, column=0, sticky="ew", pady=5)

        self.main_buttons = {
            "selpath": main_button(self.main_buttons_frame),
            "choose": main_button(self.main_buttons_frame),
            "create_tree": main_button(self.main_buttons_frame),
            "openlect": main_button(self.main_buttons_frame),
            "openlast": colored_main_button(
                self.main_buttons_frame,
                text="",
                fg_color=COLORS["button"]["green"],
                hover_color=COLORS["button_hover"]["green_h"],
            ),
            "delete": colored_main_button(
                self.main_buttons_frame,
                text="",
                fg_color=COLORS["button"]["red"],
                hover_color=COLORS["button_hover"]["red_h"],
            ),
        }
        for btn in self.main_buttons.values():
            btn.pack(pady=3)

        # Panel de progreso
        self.progress_panel = ProgressPanel(self, width=PROGRESS_W, height=135)
        self.progress_panel.grid(row=2, column=0, pady=10, sticky="n")
