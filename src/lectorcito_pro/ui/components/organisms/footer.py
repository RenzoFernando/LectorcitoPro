"""UI Organism: Footer."""

from __future__ import annotations

import customtkinter as ctk


class Footer(ctk.CTkFrame):
    def __init__(self, parent, text: str):
        super().__init__(parent, height=30, corner_radius=0)

        self.lbl = ctk.CTkLabel(self, text=text, font=("Segoe UI", 9))
        self.lbl.place(relx=0.5, rely=0.5, anchor="center")
