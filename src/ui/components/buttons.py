import customtkinter as ctk

from core.constants import BTN_H_MAIN, BTN_W_MAIN, COLORS


def create_main_buttons(parent):
    opts = {
        "width": BTN_W_MAIN,
        "height": BTN_H_MAIN,
        "corner_radius": 8,
        "font": ("Segoe UI", 11, "bold"),
        "text_color": "#FFFFFF",
    }
    buttons = {
        "selpath": ctk.CTkButton(parent, **opts),
        "choose": ctk.CTkButton(parent, **opts),
        "create_tree": ctk.CTkButton(parent, **opts),
        "openlect": ctk.CTkButton(parent, **opts),
        "openlast": ctk.CTkButton(
            parent, **opts, fg_color=COLORS["button"]["green"], hover_color=COLORS["button_hover"]["green_h"]
        ),
        "delete": ctk.CTkButton(
            parent, **opts, fg_color=COLORS["button"]["red"], hover_color=COLORS["button_hover"]["red_h"]
        ),
    }
    for btn in buttons.values():
        btn.pack(pady=3)
    return buttons
