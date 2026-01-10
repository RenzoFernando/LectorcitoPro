
from __future__ import annotations

"""Paleta de colores y constantes visuales compartidas.

Este módulo centraliza la paleta usada por la aplicación para evitar duplicación
entre la ventana principal y los diálogos.

⚠️ Importante:
- Los valores se mantienen EXACTAMENTE iguales a los que ya usaba la UI
  (no se cambia lógica de negocio).
"""

# Fuente de verdad de colores de UI.
COLORS: dict = {
    "light": {"bg": "#EBEBEB", "text": "#000000", "left_bar": "#1A1E22", "progress_bar": "#D9D9D9"},
    "dark": {"bg": "#1A1E22", "text": "#FFFFFF", "left_bar": "#EBEBEB", "progress_bar": "#333333"},
    "button": {"blue": "#3B8ED0", "green": "#3BD056", "red": "#D03B3D"},
    "button_hover": {"blue_h": "#3073A8", "green_h": "#2FA047", "red_h": "#A03031"},
    "sidebar_hover": {"light": "#3C3C3C", "dark": "#DCDCDC"},
    "progress_colors": {"start": "#3B8ED0", "mid": "#F9A825", "done": "#4CAF50"},
    # Usado por MultiFolderSelectDialog (resaltado de ítems).
    "list_item": {"selected_bg": "#3B8ED0", "normal_bg": "transparent"},
}

# Dimensiones/constantes UI (mismos valores que en la versión original).
BTN_W_MAIN: int = 275
BTN_H_MAIN: int = 31

BTN_W_ICON: int = 35
BTN_H_ICON: int = 40

SIDEBAR_WIDTH: int = 48
PROGRESS_W: int = 357
