
"""Gestión de tema (Light/Dark) para CustomTkinter.

La lógica de negocio de la app define el tema como un string:
- "Light"
- "Dark"

Este módulo centraliza la llamada a CustomTkinter para mantener coherencia
y facilitar futuros cambios (sin tocar la lógica de negocio).
"""

from __future__ import annotations

import customtkinter as ctk


def set_theme(theme: str) -> None:
    """Aplica el tema en CustomTkinter de forma segura."""
    try:
        ctk.set_appearance_mode(theme)
    except Exception:
        # No interrumpir la app si CTk no está disponible por alguna razón.
        pass
