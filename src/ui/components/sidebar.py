from tkinter import Canvas

import customtkinter as ctk

from core.constants import BTN_H_ICON, SIDEBAR_WIDTH, COLORS


def create_left_sidebar(parent):
    sidebar_height = 400
    frame = ctk.CTkFrame(parent, width=SIDEBAR_WIDTH, height=sidebar_height, corner_radius=15)
    frame.pack(expand=True, anchor="center")

    canvas = Canvas(frame, width=20, height=sidebar_height - 40, highlightthickness=0)
    canvas.place(relx=0.5, rely=0.5, anchor="center")

    return frame, canvas


def create_right_sidebar(parent, icons, current_theme: str):
    button_container = ctk.CTkFrame(parent, fg_color="transparent")
    button_container.pack(expand=True, anchor="center")

    buttons = {}
    icon_keys = ["ver", "nover", "theme_icon", "traducir", "restaurar", "github", "info"]
    for key in icon_keys:
        is_light = current_theme == "Light"
        initial_icon = icons.get("moon") if key == "theme_icon" and is_light else icons.get("sun") if key == "theme_icon" else icons.get(key)

        fg_color = COLORS["dark"]["bg"] if is_light else COLORS["light"]["bg"]
        hover_color = COLORS["sidebar_hover"]["light"] if is_light else COLORS["sidebar_hover"]["dark"]

        btn = ctk.CTkButton(
            button_container,
            image=initial_icon,
            text="",
            width=SIDEBAR_WIDTH,
            height=BTN_H_ICON,
            corner_radius=8,
            fg_color=fg_color,
            hover_color=hover_color,
        )
        btn.pack(pady=5)
        buttons[key] = btn
    return button_container, buttons
