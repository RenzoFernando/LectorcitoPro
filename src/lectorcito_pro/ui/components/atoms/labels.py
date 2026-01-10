"""UI Atoms: Labels.

Pequeñas fábricas de labels para mantener consistencia visual.
"""

from __future__ import annotations

import customtkinter as ctk


def title_label(parent, text: str = "", image=None):
    return ctk.CTkLabel(parent, text=text, image=image)


def subtitle_label(parent, text: str = "", font=("Segoe UI", 13)):
    return ctk.CTkLabel(parent, text=text, font=font)


def small_label(parent, text: str = "", font=("Segoe UI", 9), anchor: str = "w"):
    return ctk.CTkLabel(parent, text=text, font=font, anchor=anchor)
