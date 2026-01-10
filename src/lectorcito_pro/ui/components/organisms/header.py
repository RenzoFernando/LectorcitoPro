"""UI Organism: Header.

Contiene:
- Logo (label con imagen)
- Saludo (label de texto)

Se usa en `pages/home_page.py` y la ventana principal.
"""

from __future__ import annotations

import customtkinter as ctk

from ..atoms.labels import subtitle_label, title_label


class Header(ctk.CTkFrame):
    def __init__(self, parent, *, logo_image=None):
        super().__init__(parent, fg_color="transparent")

        self.lbl_title = title_label(self, text="", image=logo_image)
        self.lbl_title.pack()

        self.lbl_greet = subtitle_label(self, text="", font=("Segoe UI", 13))
        self.lbl_greet.pack()
