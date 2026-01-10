"""UI Atoms: IconButton.

Un botón de ícono (sin texto) usado en la barra lateral.
"""

from __future__ import annotations

import customtkinter as ctk

from ...theme.palette import BTN_H_ICON, SIDEBAR_WIDTH


def icon_button(
    parent,
    image=None,
    command=None,
    fg_color: str = "transparent",
    hover_color: str = "transparent",
    width: int = SIDEBAR_WIDTH,
    height: int = BTN_H_ICON,
    corner_radius: int = 8,
):
    return ctk.CTkButton(
        parent,
        image=image,
        text="",
        command=command,
        width=width,
        height=height,
        corner_radius=corner_radius,
        fg_color=fg_color,
        hover_color=hover_color,
    )
