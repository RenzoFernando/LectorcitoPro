from __future__ import annotations

import customtkinter as ctk


class Footer(ctk.CTkFrame):
    def __init__(self, parent, text: str = ""):
        super().__init__(parent, height=30, corner_radius=0)
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        self.lbl = ctk.CTkLabel(self, text=text, font=("Segoe UI", 9))
        self.lbl.grid(row=0, column=0, sticky="nsew", padx=10)
