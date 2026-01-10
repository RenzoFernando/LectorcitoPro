"""UI Atoms: Buttons.

Fábricas simples de botones reutilizables.

Importante:
- No cambia la lógica de negocio.
- Si no se especifica `fg_color/hover_color`, se deja que CustomTkinter use su tema por defecto
  (mismo comportamiento que la UI original).
"""

from __future__ import annotations

import customtkinter as ctk

from ...theme.palette import BTN_H_MAIN, BTN_W_MAIN, COLORS


def main_button(
    parent,
    text: str = "",
    command=None,
    *,
    fg_color: str | None = None,
    hover_color: str | None = None,
    text_color: str = "#FFFFFF",
):
    """Crea un botón principal con tamaño/fuente consistentes."""
    kwargs = {}
    if fg_color is not None:
        kwargs["fg_color"] = fg_color
    if hover_color is not None:
        kwargs["hover_color"] = hover_color

    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        width=BTN_W_MAIN,
        height=BTN_H_MAIN,
        corner_radius=8,
        font=("Segoe UI", 11, "bold"),
        text_color=text_color,
        **kwargs,
    )


def colored_main_button(
    parent,
    text: str,
    fg_color: str,
    hover_color: str,
    command=None,
):
    """Atajo para botones principales con color fijo."""
    return main_button(parent, text=text, command=command, fg_color=fg_color, hover_color=hover_color)


def danger_button(
    parent,
    text: str = "",
    command=None,
    *,
    width: int = 150,
    height: int = 28,
):
    """Botón de acción destructiva (ej. eliminar)."""
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        width=width,
        height=height,
        corner_radius=8,
        font=("Segoe UI", 11, "bold"),
        text_color="#FFFFFF",
        fg_color=COLORS["button"]["red"],
        hover_color=COLORS["button_hover"]["red_h"],
    )
