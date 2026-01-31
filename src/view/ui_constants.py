# src/view/ui_constants.py
import datetime

VERSION = "6.5.7"
YEAR = datetime.datetime.now().year
AUTHOR = "Renzo Fernando Mosquera Daza"
REPO_URL = "https://github.com/RenzoFernando/LectorcitoPro.git"

COLORS = {
    "light": {
        # --- Bases ---
        "bg": "#F3F4F6",
        "surface": "#FFFFFF",
        "surface_alt": "#F9FAFB",
        "footer_bg": "#EBEBEB",

        # --- Bordes y Separadores ---
        "border": "#E5E7EB",
        "card_border": "#C0C2C5",
        "separator_line": "#D1D5DB",

        # --- Texto ---
        "text": "#111827",
        "text_secondary": "#6B7280",

        # --- Componentes Laterales ---
        "left_bar": "#1A1E22",
        "sidebar_text": "#FFFFFF",

        "progress_track": "#E5E7EB",
        "progress_border": "#D1D5DB"
    },
    "dark": {
        # --- Bases ---
        "bg": "#0D1117",
        "surface": "#161B22",
        "surface_alt": "#010409",
        "footer_bg": "#12171E",

        # --- Bordes y Separadores ---
        "border": "#30363D",
        "card_border": "#30363D",
        "separator_line": "#21262D",

        # --- Texto ---
        "text": "#E6EDF3",
        "text_secondary": "#8B949E",

        # --- Componentes Laterales ---
        "left_bar": "#EBEBEB",
        "sidebar_text": "#1A1E22",

        "progress_track": "#21262D",
        "progress_border": "#30363D"
    },

    # --- Acciones (Botones Principales) ---
    "button": {
        "blue": {"bg": "#3B8ED0", "hover": "#3682BE", "border": "#2A7BB8"},
        "green": {"bg": "#32B04A", "hover": "#2D9E42", "border": "#289640"},
        "red": {"bg": "#D03B3D", "hover": "#B53032", "border": "#B02B2D"},
    },

    # --- Hover Sidebar ---
    "sidebar_hover": {
        "light": "#374151",
        "dark": "#D1D5DB"
    },

    # --- Elementos de Lista ---
    "list_item": {
        "selected_bg": "#3B8ED0",
        "normal_bg": "transparent"
    }
}

BTN_W_MAIN, BTN_H_MAIN = 315, 35
BTN_W_ICON, BTN_H_ICON = 35, 40
SIDEBAR_WIDTH = 50