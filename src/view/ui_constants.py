from app_meta import APP_VERSION, APP_AUTHOR, APP_REPOSITORY_WEB_URL, get_current_year

# =============================================================================
# CONSTANTES DE INTERFAZ
# =============================================================================

VERSION = APP_VERSION
YEAR = get_current_year()
AUTHOR = APP_AUTHOR
REPO_URL = APP_REPOSITORY_WEB_URL
FONT_FAMILY_PRIMARY = "Segoe UI"

# =============================================================================
# TOKENS DE DISEÑO
# =============================================================================
THEME_TOKENS = {
"light": {
    "bg_base": "#EDF0F4",
    "bg_elevated": "#FAFCFF",
    "bg_panel": "#F6F9FD",
    "bg_card": "#F6F9FD",
    "bg_sidebar": "#0C1420",
    "bg_dialog": "#F6F9FD",
    "bg_footer": "#F6F9FD",
    "text_primary": "#101826",
    "text_secondary": "#475569",
    "text_muted": "#6B7B92",
    "text_on_accent": "#FFFFFF",
    "neutral_white": "#FFFFFF",
    "neutral_black": "#000000",
    "tooltip_transparent_mask": "#E532F1",
    "border_subtle": "#D7E0EE",
    "border_strong": "#4A5F7E",
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

    "sidebar_pill_start": "#1C232E",
    "sidebar_pill_mid": "#1B2F49",
    "sidebar_pill_end": "#1C232E",
    "sidebar_pill_hover_start": "#386FE0",
    "sidebar_pill_hover_mid": "#5588F0",
    "sidebar_pill_hover_end": "#7569DE",

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
    "footer_bg": "#F6F9FD",
    "border": "#D6DFEE",
    "card_border": "#C8D4E8",
    "text": "#101826",
    "text_secondary_legacy": "#475569",
    "left_bar": "#0C1420",
    "sidebar_hover": "#386FE0"
},
"dark": {
    "bg_base": "#1C232E",
    "bg_elevated": "#101721",
    "bg_panel": "#0D1117",
    "bg_card": "#0D1117",
    "bg_sidebar": "#F7FAFF",
    "bg_dialog": "#0D1117",
    "bg_footer": "#0D1117",
    "text_primary": "#E9EEF7",
    "text_secondary": "#9AA7BA",
    "text_muted": "#78879B",
    "text_on_accent": "#FFFFFF",
    "neutral_white": "#FFFFFF",
    "neutral_black": "#000000",
    "tooltip_transparent_mask": "#E532F1",
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

    "sidebar_pill_start": "#EDF0F4",
    "sidebar_pill_mid": "#E6F0FF",
    "sidebar_pill_end": "#EDF0F4",
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
    "bg": "#1C232E",
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

# =============================================================================
# CONSTANTES DE INTERFAZ DERIVADAS
# =============================================================================

# Dimensiones estandar
BTN_W_MAIN, BTN_H_MAIN = 315, 35
BTN_W_ICON, BTN_H_ICON = 35, 40
SIDEBAR_WIDTH = 50

# Animaciones y transiciones
MAIN_WINDOW_SHOW_DELAY_MS = 220
MAIN_WINDOW_CENTER_RETRY_DELAY_MS = 56
MAIN_WINDOW_CENTER_MAX_ATTEMPTS = 5
MAIN_WINDOW_INITIAL_ALPHA = 0.0
MAIN_WINDOW_REVEAL_DELAY_MS = 150
MAIN_WINDOW_REVEAL_OFFSET_Y = 0
MAIN_WINDOW_REVEAL_STEP_PX = 1
MAIN_WINDOW_HIDDEN_PARK_OFFSET_PX = 150
MAIN_WINDOW_FADE_IN_STEP = 0.10
MAIN_WINDOW_FADE_IN_INTERVAL_MS = 18
MAIN_WINDOW_FADE_OUT_STEP = 0.12
MAIN_WINDOW_FADE_OUT_INTERVAL_MS = 12
MAIN_WINDOW_SOFT_REFRESH_ALPHA = 0.94
MAIN_WINDOW_SWITCH_FADE_OUT_STEP = 0.08
MAIN_WINDOW_SWITCH_FADE_OUT_INTERVAL_MS = 12
MAIN_WINDOW_SWITCH_HOLD_MS = 38
MAIN_WINDOW_SWITCH_REBUILD_DELAY_MS = 220
MAIN_WINDOW_SWITCH_FADE_IN_STEP = 0.12
MAIN_WINDOW_SWITCH_FADE_IN_INTERVAL_MS = 16
DIALOG_ICON_DELAY_MS = 95
DIALOG_PREPARE_DELAY_MS = 175
DIALOG_CENTER_RETRY_DELAY_MS = 52
DIALOG_CENTER_MAX_ATTEMPTS = 5
DIALOG_INITIAL_ALPHA = 0.0
DIALOG_REVEAL_DELAY_MS = 180
DIALOG_REVEAL_OFFSET_Y = 0
DIALOG_REVEAL_STEP_PX = 1
DIALOG_HIDDEN_PARK_OFFSET_PX = 115
DIALOG_FADE_IN_STEP = 0.09
DIALOG_FADE_IN_INTERVAL_MS = 20
DIALOG_FADE_OUT_STEP = 0.12
DIALOG_FADE_OUT_INTERVAL_MS = 12
PROFILE_SWITCH_FADE_DELAY_MS = 220
RESTORE_FADE_DELAY_MS = 260

# Tipografia
FONT_SIZE_XS = 9
FONT_SIZE_SM = 10
FONT_SIZE_MD = 11
FONT_SIZE_BASE = 12
FONT_SIZE_LG = 13
FONT_SIZE_XL = 14

# Metricas compartidas
BORDER_WIDTH_THIN = 1
BORDER_WIDTH_MEDIUM = 2
CORNER_RADIUS_SM = 10
CORNER_RADIUS_MD = 12
CORNER_RADIUS_LG = 14
CORNER_RADIUS_XL = 16
CORNER_RADIUS_2XL = 18
PADDING_XS = 4
PADDING_SM = 5
PADDING_MD = 8
PADDING_LG = 10
PADDING_XL = 12
PADDING_2XL = 15
PADDING_3XL = 18
PADDING_4XL = 20
PADDING_5XL = 24

# Ventana principal
MAIN_WINDOW_WIDTH = 600
MAIN_WINDOW_HEIGHT = 500
MAIN_WINDOW_PRELOAD_DIALOGS_EXTRA_DELAY_MS = 260
MAIN_WINDOW_BG_REFRESH_DELAY_MS = 16
MAIN_WINDOW_SIDE_PADX = 15
MAIN_WINDOW_LEFT_PADY = (0, 14)
MAIN_WINDOW_RIGHT_PADY = (0, 15)
MAIN_WINDOW_CENTER_PADY = (3, 5)
MAIN_WINDOW_HEADER_PADY = (9, 5)
MAIN_WINDOW_GREETING_FONT_SIZE = FONT_SIZE_LG
MAIN_WINDOW_GREETING_MIN_FONT_SIZE = FONT_SIZE_SM
MAIN_WINDOW_HEADER_MIN_HEIGHT = 60
MAIN_WINDOW_HEADER_TOP_INSET = 3
MAIN_WINDOW_HEADER_LOGO_TEXT_GAP = 6
MAIN_WINDOW_HEADER_TEXT_SIDE_PAD = 12
MAIN_WINDOW_HEADER_BOTTOM_INSET = 3
MAIN_WINDOW_MAIN_MENU_RADIUS = CORNER_RADIUS_2XL
MAIN_WINDOW_MAIN_MENU_BORDER_WIDTH = BORDER_WIDTH_THIN
MAIN_WINDOW_MAIN_MENU_PAD = 10
MAIN_WINDOW_MAIN_MENU_BOTTOM_GAP = 3
MAIN_WINDOW_BUTTON_FONT_SIZE = FONT_SIZE_MD
MAIN_WINDOW_BUTTON_MIN_FONT_SIZE = FONT_SIZE_SM
MAIN_WINDOW_BUTTON_MIN_WIDTH = 250
MAIN_WINDOW_BUTTON_BORDER_WIDTH = BORDER_WIDTH_MEDIUM
MAIN_WINDOW_BUTTON_SPACING = 1
MAIN_WINDOW_STATUS_AREA_PADY = (3, 5)
MAIN_WINDOW_STATUS_MIN_VISIBLE_SECONDS = 1.0
MAIN_WINDOW_FOOTER_HEIGHT = 40
MAIN_WINDOW_FOOTER_LINE_HEIGHT = 1
MAIN_WINDOW_FOOTER_FONT_SIZE = FONT_SIZE_XS
MAIN_WINDOW_TOPMOST_RESET_DELAY_MS = 90
MAIN_WINDOW_MODAL_FAIL_SAFE_DELAY_MS = 900
MAIN_WINDOW_ADAPTIVE_REFRESH_DELAY_MS = 80

# Controles compartidos de dialogos
MESSAGE_AUTO_CLOSE_SECONDS = 10
DIALOG_SECONDARY_ICON_DELAY_MS = 100
DIALOG_BUTTON_HEIGHT = 34
DIALOG_BUTTON_CORNER_RADIUS = CORNER_RADIUS_XL
DIALOG_BUTTON_FONT_SIZE = FONT_SIZE_MD
DIALOG_BUTTON_BORDER_WIDTH = BORDER_WIDTH_THIN
DIALOG_INPUT_HEIGHT = 34
DIALOG_INPUT_CORNER_RADIUS = CORNER_RADIUS_MD
DIALOG_OPTION_MENU_HEIGHT = 34
DIALOG_OPTION_MENU_CORNER_RADIUS = CORNER_RADIUS_MD
DIALOG_SCROLLABLE_BORDER_WIDTH = BORDER_WIDTH_THIN
DIALOG_CARD_BORDER_WIDTH = BORDER_WIDTH_THIN
DIALOG_CARD_CORNER_RADIUS = CORNER_RADIUS_2XL
DIALOG_CARD_PADX = 15
DIALOG_CARD_PADY = 15

# Message dialog
MESSAGE_DIALOG_TEXT_WRAP = 350
MESSAGE_DIALOG_TEXT_FONT_SIZE = FONT_SIZE_BASE
MESSAGE_DIALOG_TEXT_PADX = 20
MESSAGE_DIALOG_TEXT_PADY = (20, 20)
MESSAGE_DIALOG_OK_WIDTH = 110
MESSAGE_DIALOG_BUTTON_PADY = (0, 20)

# Confirm dialog
CONFIRM_DIALOG_TEXT_WRAP = 350
CONFIRM_DIALOG_TEXT_FONT_SIZE = FONT_SIZE_BASE
CONFIRM_DIALOG_TEXT_PADX = 20
CONFIRM_DIALOG_TEXT_PADY = (25, 25)
CONFIRM_DIALOG_BUTTON_WIDTH = 100
CONFIRM_DIALOG_BUTTON_PADX = 10
CONFIRM_DIALOG_BUTTON_FRAME_PADY = (0, 20)

# External link dialog
EXTERNAL_LINK_DIALOG_WIDTH = 430
EXTERNAL_LINK_DIALOG_HEIGHT = 240
EXTERNAL_LINK_DIALOG_TEXT_WRAP = 360
EXTERNAL_LINK_DIALOG_TEXT_FONT_SIZE = FONT_SIZE_BASE
EXTERNAL_LINK_DIALOG_TEXT_PADX = 20
EXTERNAL_LINK_DIALOG_TEXT_PADY = (24, 14)
EXTERNAL_LINK_DIALOG_TARGET_BORDER_WIDTH = BORDER_WIDTH_THIN
EXTERNAL_LINK_DIALOG_TARGET_RADIUS = CORNER_RADIUS_LG
EXTERNAL_LINK_DIALOG_TARGET_PADX = 20
EXTERNAL_LINK_DIALOG_TARGET_PADY = (0, 18)
EXTERNAL_LINK_DIALOG_TARGET_TEXT_WRAP = 330
EXTERNAL_LINK_DIALOG_TARGET_FONT_SIZE = FONT_SIZE_MD
EXTERNAL_LINK_DIALOG_TARGET_TEXT_PADX = 12
EXTERNAL_LINK_DIALOG_TARGET_TEXT_PADY = 10
EXTERNAL_LINK_DIALOG_BUTTON_WIDTH = 126
EXTERNAL_LINK_DIALOG_BUTTON_PADX = 8
EXTERNAL_LINK_DIALOG_BUTTON_FRAME_PADY = (0, 20)

# Choice dialog
CHOICE_DIALOG_WIDTH = 400
CHOICE_DIALOG_HEIGHT = 200
CHOICE_DIALOG_TEXT_WRAP = 340
CHOICE_DIALOG_TEXT_FONT_SIZE = FONT_SIZE_BASE
CHOICE_DIALOG_TEXT_PADX = 20
CHOICE_DIALOG_TEXT_PADY = (25, 15)
CHOICE_DIALOG_BUTTON_WIDTH = 220
CHOICE_DIALOG_BUTTON1_PADY = (5, 8)
CHOICE_DIALOG_BUTTON2_PADY = (0, 20)

# Profiles dialog
PROFILES_DIALOG_WIDTH = 450
PROFILES_DIALOG_HEIGHT = 500
PROFILES_DIALOG_TITLE_FONT_SIZE = FONT_SIZE_LG
PROFILES_DIALOG_TITLE_PADY = (20, 10)
PROFILES_DIALOG_SCROLL_HEIGHT = 250
PROFILES_DIALOG_SCROLL_PADX = 20
PROFILES_DIALOG_SCROLL_PADY = 10
PROFILES_DIALOG_BOTTOM_PADX = 20
PROFILES_DIALOG_BOTTOM_PADY = 20
PROFILES_DIALOG_ENTRY_PADX = (0, 10)
PROFILES_DIALOG_ADD_BUTTON_WIDTH = 40
PROFILE_ITEM_BORDER_WIDTH = BORDER_WIDTH_THIN
PROFILE_ITEM_RADIUS = CORNER_RADIUS_MD
PROFILE_ITEM_PADY = 4
PROFILE_ITEM_FONT_SIZE = FONT_SIZE_MD
PROFILE_ITEM_LABEL_PADX = 10
PROFILE_ITEM_LABEL_PADY = 8
PROFILE_ITEM_DELETE_BUTTON_SIZE = 24
PROFILE_ITEM_DELETE_PADX = 10

# Settings dialog
SETTINGS_DIALOG_WIDTH = 450
SETTINGS_DIALOG_HEIGHT = 605
SETTINGS_DIALOG_MAIN_PADX = 15
SETTINGS_DIALOG_MAIN_PADY = (15, 8)
SETTINGS_DIALOG_CONTENT_PADX = 18
SETTINGS_DIALOG_CONTENT_PADY = (18, 8)
SETTINGS_DIALOG_SECTION_FONT_SIZE = FONT_SIZE_MD
SETTINGS_DIALOG_SECTION_PADY = (0, 5)
SETTINGS_DIALOG_FORMAT_SHELL_BORDER_WIDTH = BORDER_WIDTH_THIN
SETTINGS_DIALOG_FORMAT_SHELL_RADIUS = 15
SETTINGS_DIALOG_FORMAT_SHELL_PADY = (0, 8)
SETTINGS_DIALOG_FORMAT_BUTTON_WIDTH = 84
SETTINGS_DIALOG_FORMAT_BUTTON_HEIGHT = 34
SETTINGS_DIALOG_FORMAT_BUTTON_PAD = 4
SETTINGS_DIALOG_EXE_LABEL_PADY = (10, 2)
SETTINGS_DIALOG_EXAMPLE_FONT_SIZE = FONT_SIZE_SM
SETTINGS_DIALOG_EXAMPLE_PADY = (0, 5)
SETTINGS_DIALOG_ENTRY_PADY = (0, 8)
SETTINGS_DIALOG_SEPARATOR_HEIGHT = 1
SETTINGS_DIALOG_SEPARATOR_PADY = (2, 6)
SETTINGS_DIALOG_SHORTCUTS_LABEL_PADY = (4, 8)
SETTINGS_DIALOG_SHORTCUT_BUTTON_PADY = 3
SETTINGS_DIALOG_SHORTCUT_LAST_BUTTON_PADY = (3, 0)
SETTINGS_DIALOG_TRANSFER_LABEL_PADY = (10, 8)
SETTINGS_DIALOG_TRANSFER_DESC_FONT_SIZE = FONT_SIZE_SM
SETTINGS_DIALOG_TRANSFER_DESC_PADY = (0, 8)
SETTINGS_DIALOG_TRANSFER_BUTTON_PADY = 3
SETTINGS_DIALOG_TRANSFER_LAST_BUTTON_PADY = (3, 10)
SETTINGS_DIALOG_FOOTER_BORDER_WIDTH = BORDER_WIDTH_THIN
SETTINGS_DIALOG_FOOTER_RADIUS = CORNER_RADIUS_XL
SETTINGS_DIALOG_FOOTER_HEIGHT = 58
SETTINGS_DIALOG_FOOTER_PADX = 18
SETTINGS_DIALOG_FOOTER_PADY = (0, 16)
SETTINGS_DIALOG_CLOSE_BUTTON_WIDTH = 126
SETTINGS_DIALOG_CLOSE_BUTTON_HEIGHT = 36
SETTINGS_DIALOG_CLOSE_BUTTON_PADY = (0, 0)
SETTINGS_DIALOG_TOGGLE_RADIUS = CORNER_RADIUS_MD
SETTINGS_DIALOG_TOGGLE_BORDER_WIDTH = BORDER_WIDTH_THIN
SETTINGS_DIALOG_TOGGLE_FONT_SIZE = FONT_SIZE_MD

# Status panel
STATUS_PANEL_DEFAULT_MIN_VISIBLE_SECONDS = 2.0
STATUS_PANEL_CORNER_RADIUS = CORNER_RADIUS_XL
STATUS_PANEL_BORDER_WIDTH = BORDER_WIDTH_THIN
STATUS_PANEL_PADX = 10
STATUS_PANEL_PADY = (4, 6)
STATUS_PANEL_ROW_PADX = 12
STATUS_PANEL_TOP_ROW_PADY = (10, 4)
STATUS_PANEL_STATUS_FONT_SIZE = FONT_SIZE_MD
STATUS_PANEL_PERCENT_FONT_SIZE = FONT_SIZE_MD
STATUS_PANEL_PERCENT_PADX = (0, 8)
STATUS_PANEL_CANCEL_SIZE = 28
STATUS_PANEL_CANCEL_RADIUS = CORNER_RADIUS_LG
STATUS_PANEL_CANCEL_FONT_SIZE = FONT_SIZE_LG
STATUS_PANEL_PROGRESS_HEIGHT = 12
STATUS_PANEL_PROGRESS_RADIUS = 8
STATUS_PANEL_PROGRESS_PADY = (0, 6)
STATUS_PANEL_FILE_ROW_PADY = (0, 12)
STATUS_PANEL_FILE_PREFIX_FONT_SIZE = FONT_SIZE_XS
STATUS_PANEL_FILE_TEXT_FONT_SIZE = FONT_SIZE_XS
STATUS_PANEL_FILE_WRAP_DEFAULT = 460
STATUS_PANEL_MIN_USABLE_WIDTH = 180
STATUS_PANEL_PREFIX_GAP = 6
STATUS_PANEL_MIN_WRAP = 160
STATUS_PANEL_DOTS_INTERVAL_MS = 450
STATUS_PANEL_PROGRESS_TICK_MS = 16
STATUS_PANEL_SUCCESS_RESET_DELAY_MS = 900
STATUS_PANEL_ELLIPSIS_MAX_LEN = 72
STATUS_PANEL_CONTEXT_MAX_LEN = 140

# Tags dialog
TAGS_DIALOG_WIDTH = 600
TAGS_DIALOG_HEIGHT = 600
TAGS_DIALOG_TAG_FONT_SIZE = FONT_SIZE_SM
TAGS_DIALOG_EXTRA_CHECKBOX_PADX = 20
TAGS_DIALOG_EXTRA_CHECKBOX_PADY = (10, 0)
TAGS_DIALOG_SEPARATOR_HEIGHT = 1
TAGS_DIALOG_SEPARATOR_PADY = (10, 0)
TAGS_DIALOG_BUTTON_FRAME_PADY = (15, 10)
TAGS_DIALOG_ACTION_BUTTON_WIDTH = 100
TAGS_DIALOG_ACTION_BUTTON_PADX = 10
TAGS_DIALOG_LAYOUT_REFRESH_DELAY_MS = 30
TAGS_DIALOG_SECTION_LABEL_FONT_SIZE = FONT_SIZE_MD
TAGS_DIALOG_SECTION_LABEL_PADY = (10, 2)
TAGS_DIALOG_SECTION_LABEL_PADX = 20
TAGS_DIALOG_SCROLL_PADX = 20
TAGS_DIALOG_INPUT_PADX = 20
TAGS_DIALOG_INPUT_PADY = (5, 0)
TAGS_DIALOG_AUTODETECT_BUTTON_WIDTH = 80
TAGS_DIALOG_AUTODETECT_BUTTON_HEIGHT = 28
TAGS_DIALOG_AUTODETECT_BUTTON_PADX = (8, 0)
TAGS_DIALOG_ROW_PADY = (0, 5)
TAGS_DIALOG_PILL_SPACING = 6
TAGS_DIALOG_WRAP_SAFETY_PX = 16
TAGS_DIALOG_PILL_RADIUS = CORNER_RADIUS_LG
TAGS_DIALOG_PILL_LABEL_PADX = (10, 4)
TAGS_DIALOG_PILL_LABEL_PADY = 2
TAGS_DIALOG_PILL_CLOSE_SIZE = 20
TAGS_DIALOG_PILL_CLOSE_RADIUS = CORNER_RADIUS_SM
TAGS_DIALOG_PILL_CLOSE_PADX = (0, 8)
TAGS_DIALOG_PILL_CLOSE_PADY = 3

# Tooltip
TOOLTIP_FRAME_CORNER_RADIUS = CORNER_RADIUS_MD
TOOLTIP_FRAME_BORDER_WIDTH = BORDER_WIDTH_MEDIUM
TOOLTIP_FONT_SIZE = FONT_SIZE_SM
TOOLTIP_WRAP_LENGTH = 260
TOOLTIP_LABEL_PADX = 12
TOOLTIP_LABEL_PADY = 8
TOOLTIP_FADE_IN_STEP = 0.12
TOOLTIP_FADE_OUT_STEP = 0.14
TOOLTIP_FADE_INTERVAL_MS = 12
TOOLTIP_AUTOHIDE_SECONDS = 2.5
TOOLTIP_DEFAULT_DELAY_MS = 500
TOOLTIP_DEFAULT_GAP = 10
TOOLTIP_WINDOW_PAD = 8
TOOLTIP_FALLBACK_WIDTH = 240
TOOLTIP_FALLBACK_HEIGHT = 40

# Recursos visuales
SIDEBAR_ICON_SIZE = (30, 30)
THEME_TOGGLE_ICON_SIZE = (32, 32)
LOGO_TARGET_WIDTH = 165

# Sidebars
LEFT_SIDEBAR_HEIGHT = 415
LEFT_SIDEBAR_FONT_SIZE = FONT_SIZE_BASE
PILL_TEXT_BUTTON_FONT_SIZE = FONT_SIZE_MD
SIDEBAR_REPAINT_DELAY_MS = 16
SIDEBAR_CLICK_LOCK_DELAY_MS = 220
PILL_TEXT_HORIZONTAL_INSET = 16
RIGHT_SIDEBAR_BUTTON_SPACING = 1
RIGHT_SIDEBAR_BUTTON_BORDER_WIDTH = BORDER_WIDTH_THIN

# Progress bar
PROGRESS_CANVAS_TICK_MS = 16
PROGRESS_CAPSULE_SEGMENTS = 20
PROGRESS_MIN_BODY_SEGMENTS = 24
PROGRESS_POINT_SEGMENTS = 12

TAGS_DIALOG_SCROLL_BORDER_WIDTH = BORDER_WIDTH_THIN


# =============================================================================
# CONSTANTES DERIVADAS
# =============================================================================
NEUTRAL_WHITE = THEME_TOKENS["light"]["neutral_white"]
NEUTRAL_BLACK = THEME_TOKENS["light"]["neutral_black"]
TOOLTIP_TRANSPARENT_COLOR = THEME_TOKENS["light"]["tooltip_transparent_mask"]
PROGRESS_DEFAULT_TRACK = THEME_TOKENS["light"]["progress_track"]
PROGRESS_DEFAULT_BORDER = THEME_TOKENS["light"]["progress_border"]
PROGRESS_DEFAULT_STOPS = [
(0.00, THEME_TOKENS["light"]["progress_gradient_start"]),
(0.50, THEME_TOKENS["light"]["progress_gradient_mid"]),
(1.00, THEME_TOKENS["light"]["progress_gradient_end"]),
]


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
