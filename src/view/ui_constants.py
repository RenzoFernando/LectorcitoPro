from app_meta import APP_VERSION, APP_AUTHOR, APP_REPOSITORY_WEB_URL, get_current_year
# =============================================================================
# CONSTANTES DE INTERFAZ
# =============================================================================

VERSION = APP_VERSION
YEAR = get_current_year()
AUTHOR = APP_AUTHOR
REPO_URL = APP_REPOSITORY_WEB_URL

# Definicion de paletas de colores para temas Claro/Oscuro
THEME_TOKENS = {
    "light": {
        "bg_base": "#F4F6FB",
        "bg_elevated": "#FFFFFF",
        "bg_panel": "#FBFCFF",
        "bg_card": "#FFFFFF",
        "bg_sidebar": "#162235",
        "bg_dialog": "#FFFFFF",
        "bg_footer": "#EAF0F7",
        "text_primary": "#101826",
        "text_secondary": "#475569",
        "text_muted": "#6B7B92",
        "text_on_accent": "#FFFFFF",
        "border_subtle": "#D6DCEB",
        "border_strong": "#C0CEE3",
        "separator_line": "#D8DFEE",
        "accent_blue": "#2F6FE4",
        "accent_blue_hover": "#255FD0",
        "accent_purple": "#6E63DA",
        "accent_blue_purple_gradient_start": "#2F6FE4",
        "accent_blue_purple_gradient_mid": "#4A7FF1",
        "accent_blue_purple_gradient_end": "#6E63DA",
        "success_green": "#2E9D46",
        "success_green_deep": "#237837",
        "success_green_mid": "#45B86B",
        "danger_red": "#C23A3C",
        "danger_red_deep": "#9F2E30",
        "danger_red_mid": "#D45A5D",
        "sidebar_pill_start": "#162235",
        "sidebar_pill_end": "#243754",
        "sidebar_pill_hover_start": "#2F6FE4",
        "sidebar_pill_hover_end": "#6E63DA",
        "sidebar_text": "#FFFFFF",
        "progress_track": "#DCE4F2",
        "progress_border": "#C7D3E8",
        "progress_gradient_start": "#2F6FE4",
        "progress_gradient_mid": "#4A7FF1",
        "progress_gradient_end": "#6E63DA",
        "glow_blue_soft": "#D9E7FF",
        "glow_purple_soft": "#E8DEFF",
        "shadow_soft": "#B7C5DE",
        "shadow_strong": "#7E93BC",
        "bg": "#F4F6FB",
        "surface": "#FFFFFF",
        "surface_alt": "#FBFCFF",
        "footer_bg": "#EAF0F7",
        "border": "#D6DCEB",
        "card_border": "#C0CEE3",
        "text": "#101826",
        "text_secondary_legacy": "#475569",
        "left_bar": "#162235",
        "sidebar_hover": "#243754"
    },
    "dark": {
        "bg_base": "#0A1019",
        "bg_elevated": "#121A25",
        "bg_panel": "#0F1722",
        "bg_card": "#182233",
        "bg_sidebar": "#172133",
        "bg_dialog": "#111A28",
        "bg_footer": "#101722",
        "text_primary": "#E7EDF7",
        "text_secondary": "#97A5BB",
        "text_muted": "#73839D",
        "text_on_accent": "#FFFFFF",
        "border_subtle": "#233146",
        "border_strong": "#314563",
        "separator_line": "#223147",
        "accent_blue": "#4A7FF1",
        "accent_blue_hover": "#5B8DF5",
        "accent_purple": "#7C72E8",
        "accent_blue_purple_gradient_start": "#3D76EC",
        "accent_blue_purple_gradient_mid": "#5A8AF4",
        "accent_blue_purple_gradient_end": "#7C72E8",
        "success_green": "#35B25A",
        "success_green_deep": "#2A8D46",
        "success_green_mid": "#47C76B",
        "danger_red": "#D2505B",
        "danger_red_deep": "#A53B45",
        "danger_red_mid": "#E16E78",
        "sidebar_pill_start": "#172133",
        "sidebar_pill_end": "#22314B",
        "sidebar_pill_hover_start": "#3D76EC",
        "sidebar_pill_hover_end": "#7C72E8",
        "sidebar_text": "#EEF3FB",
        "progress_track": "#1B2637",
        "progress_border": "#293C58",
        "progress_gradient_start": "#3D76EC",
        "progress_gradient_mid": "#5A8AF4",
        "progress_gradient_end": "#7C72E8",
        "glow_blue_soft": "#1C355E",
        "glow_purple_soft": "#261F56",
        "shadow_soft": "#07101D",
        "shadow_strong": "#030813",
        "bg": "#0A1019",
        "surface": "#121A25",
        "surface_alt": "#0F1722",
        "footer_bg": "#101722",
        "border": "#233146",
        "card_border": "#314563",
        "text": "#E7EDF7",
        "text_secondary_legacy": "#97A5BB",
        "left_bar": "#172133",
        "sidebar_hover": "#22314B"
    }
}

BUTTON_TOKENS = {
    "blue": {
        "bg": "#3D76EC",
        "hover": "#315FD5",
        "border": "#5A8AF4",
        "text": "#FFFFFF",
        "gradient_start": "#2F6FE4",
        "gradient_mid": "#4A7FF1",
        "gradient_end": "#6E63DA",
        "hover_gradient_start": "#255FD0",
        "hover_gradient_mid": "#3F71E8",
        "hover_gradient_end": "#5F57CA"
    },
    "green": {
        "bg": "#2E9D46",
        "hover": "#247F39",
        "border": "#4CBD6A",
        "text": "#FFFFFF",
        "gradient_start": "#237837",
        "gradient_mid": "#2E9D46",
        "gradient_end": "#45B86B",
        "hover_gradient_start": "#1E662F",
        "hover_gradient_mid": "#27873D",
        "hover_gradient_end": "#3DAA5E"
    },
    "red": {
        "bg": "#C23A3C",
        "hover": "#A73032",
        "border": "#D55B5D",
        "text": "#FFFFFF",
        "gradient_start": "#9F2E30",
        "gradient_mid": "#C23A3C",
        "gradient_end": "#D45A5D",
        "hover_gradient_start": "#8A272A",
        "hover_gradient_mid": "#A73134",
        "hover_gradient_end": "#C44C50"
    },
    "neutral": {
        "bg": "#384A68",
        "hover": "#2E3D56",
        "border": "#506382",
        "text": "#FFFFFF"
    }
}

COLORS = {
    "light": {
        **THEME_TOKENS["light"],
        "text_secondary": THEME_TOKENS["light"]["text_secondary"],
    },
    "dark": {
        **THEME_TOKENS["dark"],
        "text_secondary": THEME_TOKENS["dark"]["text_secondary"],
    },
    "button": BUTTON_TOKENS,
    "sidebar_hover": {
        "light": THEME_TOKENS["light"]["sidebar_pill_hover_start"],
        "dark": THEME_TOKENS["dark"]["sidebar_pill_hover_start"]
    },
    "list_item": {
        "selected_bg": THEME_TOKENS["light"]["accent_blue"],
        "normal_bg": "transparent"
    }
}


def resolve_theme_name(theme_name: str | None) -> str:
    if isinstance(theme_name, str) and theme_name.lower() == "dark":
        return "dark"
    return "light"


def get_theme_tokens(theme_name: str | None) -> dict:
    return THEME_TOKENS[resolve_theme_name(theme_name)]


def get_button_tokens(button_name: str = "blue") -> dict:
    return BUTTON_TOKENS.get(button_name, BUTTON_TOKENS["blue"])


def get_color_pair(token_name: str) -> tuple[str, str]:
    return THEME_TOKENS["light"][token_name], THEME_TOKENS["dark"][token_name]


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = (value or "").strip().lstrip("#")
    if len(value) != 6:
        return 0, 0, 0
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def mix_color(color_a: str, color_b: str, ratio: float) -> str:
    ratio = max(0.0, min(1.0, float(ratio)))
    ar, ag, ab = hex_to_rgb(color_a)
    br, bg, bb = hex_to_rgb(color_b)
    return rgb_to_hex((
        int(ar + (br - ar) * ratio),
        int(ag + (bg - ag) * ratio),
        int(ab + (bb - ab) * ratio),
    ))


def with_alpha(color: str, alpha: int) -> tuple[int, int, int, int]:
    r, g, b = hex_to_rgb(color)
    return r, g, b, max(0, min(255, int(alpha)))


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
