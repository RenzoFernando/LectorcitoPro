"""UI Molecule: Progress Bar + Labels.

Encapsula los widgets de progreso para evitar repetir creación/estilos.
"""

from __future__ import annotations

from dataclasses import dataclass

import customtkinter as ctk


@dataclass
class ProgressWidgets:
    lbl_status: ctk.CTkLabel
    lbl_percent: ctk.CTkLabel
    bar: ctk.CTkProgressBar
    lbl_current_file: ctk.CTkLabel

    @classmethod
    def build(cls, parent) -> "ProgressWidgets":
        lbl_status = ctk.CTkLabel(parent, text="", font=("Segoe UI", 11, "bold"))
        lbl_percent = ctk.CTkLabel(parent, text="", font=("Segoe UI", 11, "bold"))
        bar = ctk.CTkProgressBar(parent, height=10, corner_radius=8, mode="determinate")
        bar.set(0)
        lbl_current_file = ctk.CTkLabel(parent, text="", font=("Segoe UI", 9), anchor="w")
        return cls(lbl_status=lbl_status, lbl_percent=lbl_percent, bar=bar, lbl_current_file=lbl_current_file)

    def hide_all(self) -> None:
        for w in (self.lbl_status, self.lbl_percent, self.bar, self.lbl_current_file):
            try:
                w.grid_forget()
            except Exception:
                pass
