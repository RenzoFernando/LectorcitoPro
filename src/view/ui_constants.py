from app_meta import APP_VERSION, APP_AUTHOR, APP_REPOSITORY_WEB_URL, get_current_year
# =============================================================================
# CONSTANTES DE INTERFAZ
# =============================================================================

VERSION = APP_VERSION
YEAR = get_current_year()
AUTHOR = APP_AUTHOR
REPO_URL = APP_REPOSITORY_WEB_URL

# Definicion de paletas de colores para temas Claro/Oscuro
COLORS = {
    "light": {
        # Bases
        "bg": "#F3F4F6",
        "surface": "#FFFFFF",
        "surface_alt": "#F9FAFB",
        "footer_bg": "#EBEBEB",

        # Bordes
        "border": "#E5E7EB",
        "card_border": "#C0C2C5",
        "separator_line": "#D1D5DB",

        # Texto
        "text": "#111827",
        "text_secondary": "#6B7280",

        # Componentes
        "left_bar": "#1A1E22",
        "sidebar_text": "#FFFFFF",
        "progress_track": "#E5E7EB",
        "progress_border": "#D1D5DB"
    },
    "dark": {
        # Bases
        "bg": "#0D1117",
        "surface": "#161B22",
        "surface_alt": "#010409",
        "footer_bg": "#12171E",

        # Bordes
        "border": "#30363D",
        "card_border": "#30363D",
        "separator_line": "#21262D",

        # Texto
        "text": "#E6EDF3",
        "text_secondary": "#8B949E",

        # Componentes
        "left_bar": "#EBEBEB",
        "sidebar_text": "#1A1E22",
        "progress_track": "#21262D",
        "progress_border": "#30363D"
    },

    # Botones de accion (compartidos)
    "button": {
        "blue": {"bg": "#3B8ED0", "hover": "#3682BE", "border": "#2A7BB8"},
        "green": {"bg": "#32B04A", "hover": "#2D9E42", "border": "#289640"},
        "red": {"bg": "#D03B3D", "hover": "#B53032", "border": "#B02B2D"},
    },

    "sidebar_hover": {
        "light": "#374151",
        "dark": "#D1D5DB"
    },

    "list_item": {
        "selected_bg": "#3B8ED0",
        "normal_bg": "transparent"
    }
}

# Dimensiones estandar
BTN_W_MAIN, BTN_H_MAIN = 315, 35
BTN_W_ICON, BTN_H_ICON = 35, 40
SIDEBAR_WIDTH = 50

# Animaciones y transiciones
MAIN_WINDOW_SHOW_DELAY_MS = 220
MAIN_WINDOW_CENTER_RETRY_DELAY_MS = 56
MAIN_WINDOW_CENTER_MAX_ATTEMPTS = 5
MAIN_WINDOW_INITIAL_ALPHA = 0.0
MAIN_WINDOW_REVEAL_OFFSET_Y = 0
MAIN_WINDOW_REVEAL_STEP_PX = 1
MAIN_WINDOW_FADE_IN_STEP = 0.10
MAIN_WINDOW_FADE_IN_INTERVAL_MS = 18
MAIN_WINDOW_FADE_OUT_STEP = 0.12
MAIN_WINDOW_FADE_OUT_INTERVAL_MS = 12
MAIN_WINDOW_SOFT_REFRESH_ALPHA = 0.94
MAIN_WINDOW_SWITCH_FADE_OUT_STEP = 0.08
MAIN_WINDOW_SWITCH_FADE_OUT_INTERVAL_MS = 12
MAIN_WINDOW_SWITCH_HOLD_MS = 38
MAIN_WINDOW_SWITCH_FADE_IN_STEP = 0.12
MAIN_WINDOW_SWITCH_FADE_IN_INTERVAL_MS = 16
DIALOG_ICON_DELAY_MS = 95
DIALOG_PREPARE_DELAY_MS = 175
DIALOG_CENTER_RETRY_DELAY_MS = 52
DIALOG_CENTER_MAX_ATTEMPTS = 5
DIALOG_INITIAL_ALPHA = 0.0
DIALOG_REVEAL_OFFSET_Y = 0
DIALOG_REVEAL_STEP_PX = 1
DIALOG_FADE_IN_STEP = 0.09
DIALOG_FADE_IN_INTERVAL_MS = 20
DIALOG_FADE_OUT_STEP = 0.12
DIALOG_FADE_OUT_INTERVAL_MS = 12
PROFILE_SWITCH_FADE_DELAY_MS = 220
RESTORE_FADE_DELAY_MS = 260