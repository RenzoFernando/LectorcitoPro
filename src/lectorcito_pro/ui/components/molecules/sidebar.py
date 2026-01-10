"""UI Molecule: Sidebars.

Este archivo contiene componentes de UI reutilizables para:
- Barra lateral izquierda (Canvas con texto rotado).
- Barra lateral derecha (botones con íconos).

Se integra con `ui/app_window/main_window.py` sin cambiar la lógica de negocio.
"""

from __future__ import annotations

from tkinter import Canvas

import customtkinter as ctk

from ..atoms.icon_button import icon_button
from ...theme.palette import BTN_H_ICON, COLORS, SIDEBAR_WIDTH


class LeftSidebar(ctk.CTkFrame):
    """Sidebar izquierda: panel con Canvas y texto rotado."""

    def __init__(self, parent, height: int = 400, corner_radius: int = 15):
        super().__init__(
            parent,
            width=SIDEBAR_WIDTH,
            height=height,
            corner_radius=corner_radius,
        )
        self.pack_propagate(False)

        self.canvas = Canvas(self, width=20, height=max(1, height - 40), highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center")

    def paint_text(self, text: str, current_theme: str) -> None:
        """Pinta el texto vertical en el canvas."""
        self.canvas.delete("all")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            return

        color = COLORS["dark"]["text"] if current_theme == "Light" else COLORS["light"]["text"]
        self.canvas.create_text(
            w / 2,
            h / 2,
            text=text,
            angle=90,
            font=("Segoe UI", 10, "bold"),
            fill=color,
        )


class RightSidebar(ctk.CTkFrame):
    """Sidebar derecha: conjunto de botones con íconos."""

    def __init__(
        self,
        parent,
        icons: dict,
        current_theme: str,
        icon_keys: list[str] | None = None,
    ):
        super().__init__(parent, fg_color="transparent")

        self.icons = icons or {}
        self.current_theme = current_theme
        self.icon_keys = icon_keys or ["ver", "nover", "theme_icon", "traducir", "restaurar", "github", "info"]

        button_container = ctk.CTkFrame(self, fg_color="transparent")
        button_container.pack(expand=True, anchor="center")

        self.buttons: dict[str, ctk.CTkButton] = {}
        self._build_buttons(button_container)

    def _build_buttons(self, container):
        self.buttons.clear()

        is_light = self.current_theme == "Light"
        fg_color = COLORS["dark"]["bg"] if is_light else COLORS["light"]["bg"]
        hover_color = COLORS["sidebar_hover"]["light"] if is_light else COLORS["sidebar_hover"]["dark"]

        for key in self.icon_keys:
            # Icono inicial del toggle de tema
            if key == "theme_icon":
                image = self.icons.get("moon") if is_light else self.icons.get("sun")
            else:
                image = self.icons.get(key)

            btn = icon_button(
                container,
                image=image,
                fg_color=fg_color,
                hover_color=hover_color,
                width=SIDEBAR_WIDTH,
                height=BTN_H_ICON,
                corner_radius=8,
            )
            btn.pack(pady=5)
            self.buttons[key] = btn

    def update_theme(self, current_theme: str) -> None:
        """Actualiza colores e íconos cuando cambia el tema."""
        self.current_theme = current_theme
        is_light = self.current_theme == "Light"
        fg_color = COLORS["dark"]["bg"] if is_light else COLORS["light"]["bg"]
        hover_color = COLORS["sidebar_hover"]["light"] if is_light else COLORS["sidebar_hover"]["dark"]

        for key, btn in self.buttons.items():
            if key == "theme_icon":
                btn.configure(image=self.icons.get("moon") if is_light else self.icons.get("sun"))
            btn.configure(fg_color=fg_color, hover_color=hover_color)
