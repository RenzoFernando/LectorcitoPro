from __future__ import annotations

import customtkinter as ctk

from ...theme.palette import BTN_W_MAIN, BTN_H_MAIN


def main_button(parent, text: str, command=None, *, width: int = BTN_W_MAIN, height: int = BTN_H_MAIN, **kwargs):
    """Botón principal con tamaño consistente."""
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        width=width,
        height=height,
        corner_radius=8,
        font=("Segoe UI", 11, "bold"),
        **kwargs,
    )


def colored_main_button(
    parent,
    text: str,
    command=None,
    *,
    fg_color: str,
    hover_color: str,
    text_color: str = "#FFFFFF",
    width: int = BTN_W_MAIN,
    height: int = BTN_H_MAIN,
    **kwargs,
):
    """Botón principal (mismo tamaño) pero con colores custom (verde/rojo/etc)."""
    return main_button(
        parent,
        text=text,
        command=command,
        width=width,
        height=height,
        fg_color=fg_color,
        hover_color=hover_color,
        text_color=text_color,
        **kwargs,
    )
