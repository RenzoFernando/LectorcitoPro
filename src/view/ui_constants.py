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
        "bg_base": "#EDF0F4",
        "bg_elevated": "#FAFCFF",
        "bg_panel": "#F6F9FD",
        "bg_card": "#FBFDFF",
        "bg_sidebar": "#0D1117",
        "bg_dialog": "#FBFDFF",
        "bg_footer": "#EBEBEB",
        "text_primary": "#101826",
        "text_secondary": "#475569",
        "text_muted": "#6B7B92",
        "text_on_accent": "#FFFFFF",
        "border_subtle": "#D7E0EE",
        "border_strong": "#415470",
        "separator_line": "#DDE5F1",
        "accent_blue": "#2F6FE4",
        "accent_blue_hover": "#255FD0",
        "accent_purple": "#6E63DA",
        "accent_blue_purple_gradient_start": "#2F6FE4",
        "accent_blue_purple_gradient_mid": "#4A7FF1",
        "accent_blue_purple_gradient_end": "#6E63DA",
        "success_green": "#32B04A",
        "success_green_deep": "#27883A",
        "success_green_mid": "#3FB95A",
        "danger_red": "#D03B3D",
        "danger_red_deep": "#A73335",
        "danger_red_mid": "#D94D50",
        "sidebar_pill_start": "#0D1117",
        "sidebar_pill_mid": "#142033",
        "sidebar_pill_end": "#1B2A42",
        "sidebar_pill_hover_start": "#2F6FE4",
        "sidebar_pill_hover_mid": "#4A7FF1",
        "sidebar_pill_hover_end": "#6E63DA",
        "sidebar_text": "#FFFFFF",
        "progress_track": "#DCE5F3",
        "progress_border": "#C8D4E7",
        "progress_gradient_start": "#2F6FE4",
        "progress_gradient_mid": "#4A7FF1",
        "progress_gradient_end": "#6E63DA",
        "glow_blue_soft": "#D6E5FF",
        "glow_purple_soft": "#ECE7FF",
        "shadow_soft": "#BCCBDD",
        "shadow_strong": "#8799B4",
        "bg": "#EDF0F4",
        "surface": "#FFFFFF",
        "surface_alt": "#F8FBFF",
        "footer_bg": "#EBEBEB",
        "border": "#D6DFEE",
        "card_border": "#C8D4E8",
        "text": "#101826",
        "text_secondary_legacy": "#475569",
        "left_bar": "#0D1117",
        "sidebar_hover": "#2F6FE4"
    },
    "dark": {
        "bg_base": "#0D1117",
        "bg_elevated": "#101721",
        "bg_panel": "#111A25",
        "bg_card": "#121D2A",
        "bg_sidebar": "#F7FAFF",
        "bg_dialog": "#111A25",
        "bg_footer": "#161B22",
        "text_primary": "#E9EEF7",
        "text_secondary": "#9AA7BA",
        "text_muted": "#78879B",
        "text_on_accent": "#FFFFFF",
        "border_subtle": "#1A2638",
        "border_strong": "#C7D5EA",
        "separator_line": "#1D2A3D",
        "accent_blue": "#4E82F3",
        "accent_blue_hover": "#5C8DF5",
        "accent_purple": "#8075E9",
        "accent_blue_purple_gradient_start": "#4077EA",
        "accent_blue_purple_gradient_mid": "#5D8DF3",
        "accent_blue_purple_gradient_end": "#7E75E8",
        "success_green": "#32B04A",
        "success_green_deep": "#27883A",
        "success_green_mid": "#3FB95A",
        "danger_red": "#D03B3D",
        "danger_red_deep": "#A73335",
        "danger_red_mid": "#D94D50",
        "sidebar_pill_start": "#FBFDFF",
        "sidebar_pill_mid": "#E6F0FF",
        "sidebar_pill_end": "#C7D8F2",
        "sidebar_pill_hover_start": "#2F6FE4",
        "sidebar_pill_hover_mid": "#4A7FF1",
        "sidebar_pill_hover_end": "#6E63DA",
        "sidebar_text": "#122036",
        "progress_track": "#162131",
        "progress_border": "#25364F",
        "progress_gradient_start": "#3D76EC",
        "progress_gradient_mid": "#5A8AF4",
        "progress_gradient_end": "#7C72E8",
        "glow_blue_soft": "#112745",
        "glow_purple_soft": "#1F1C40",
        "shadow_soft": "#050A10",
        "shadow_strong": "#02060A",
        "bg": "#0D1117",
        "surface": "#111A27",
        "surface_alt": "#121C2B",
        "footer_bg": "#161B22",
        "border": "#202D42",
        "card_border": "#2A3C56",
        "text": "#E9EEF7",
        "text_secondary_legacy": "#9AA7BA",
        "left_bar": "#F7FAFF",
        "sidebar_hover": "#2F6FE4"
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
        "bg": "#32B04A",
        "hover": "#2A9540",
        "border": "#52C86B",
        "text": "#FFFFFF",
        "gradient_start": "#27883A",
        "gradient_mid": "#32B04A",
        "gradient_end": "#3AAE54",
        "hover_gradient_start": "#226F31",
        "hover_gradient_mid": "#2A9540",
        "hover_gradient_end": "#338E48"
    },
    "red": {
        "bg": "#D03B3D",
        "hover": "#B33537",
        "border": "#E06163",
        "text": "#FFFFFF",
        "gradient_start": "#A73335",
        "gradient_mid": "#D03B3D",
        "gradient_end": "#C94A4C",
        "hover_gradient_start": "#8F2D2E",
        "hover_gradient_mid": "#B33537",
        "hover_gradient_end": "#AA4143"
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


