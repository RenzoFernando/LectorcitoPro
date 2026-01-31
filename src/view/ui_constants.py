# src/view/ui_constants.py
import datetime

VERSION = "6.4.1"
YEAR = datetime.datetime.now().year
AUTHOR = "Renzo Fernando Mosquera Daza"
REPO_URL = "https://github.com/RenzoFernando/LectorcitoPro.git"

COLORS = {
    "light": {
        "bg": "#EBEBEB",        # Fondo ventana principal
        "text": "#000000",
        "left_bar": "#1A1E22",
        "card": "#FFFFFF",      # Fondo tarjeta (diálogos)
        "card_border": "#D0D7DE",
        "inner_area": "#F2F4F7", # <--- NUEVO: Gris azulado muy suave para listas internas (contraste con blanco)
        "progress_bar": "#D9D9D9"
    },
    "dark": {
        "bg": "#1A1E22",        # Fondo ventana principal
        "text": "#FFFFFF",
        "left_bar": "#EBEBEB",
        "card": "#21262D",      # Fondo tarjeta (diálogos)
        "card_border": "#30363D",
        "inner_area": "#161B22", # <--- NUEVO: Más oscuro que la tarjeta para dar profundidad
        "progress_bar": "#333333"
    },
    "button": {
        "blue": "#3B8ED0",
        "green": "#3BD056",
        "red": "#D03B3D"
    },
    "button_hover": {
        "blue_h": "#3073A8",
        "green_h": "#2FA047",
        "red_h": "#A03031"
    },
    "sidebar_hover": {
        "light": "#3C3C3C",
        "dark": "#DCDCDC"
    },
    "progress_colors": {
        "start": "#3B8ED0",
        "mid": "#F9A825",
        "done": "#4CAF50"
    },
    "list_item": {
        "selected_bg": "#3B8ED0",
        "normal_bg": "transparent"
    }
}

BTN_W_MAIN, BTN_H_MAIN = 315, 35
BTN_W_ICON, BTN_H_ICON = 35, 40
SIDEBAR_WIDTH = 50