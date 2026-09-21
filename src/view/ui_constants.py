import sys

from app_meta import APP_AUTHOR, APP_REPOSITORY_WEB_URL, APP_VERSION

# =============================================================================
# CONSTANTES DE INTERFAZ
# =============================================================================

VERSION = APP_VERSION
AUTHOR = APP_AUTHOR
REPO_URL = APP_REPOSITORY_WEB_URL
FONT_FAMILY_PRIMARY = "Segoe UI" if sys.platform.startswith("win") else "DejaVu Sans"

# Escala visual global solicitada para esta iteracion.
UI_DENSITY_SCALE = 0.90


# =============================================================================
# TOKENS DE DISEÑO
# =============================================================================

THEME_TOKENS = {
    "light": {
        "bg_base": "#F8FAFC",
        "bg_elevated": "#FFFFFF",
        "bg_panel": "#FFFFFF",
        "bg_card": "#FFFFFF",
        "bg_sidebar": "#FFFFFF",
        "bg_dialog": "#F8FAFC",
        "bg_footer": "#FFFFFF",
        "surface_alt": "#F1F5F9",
        "text_primary": "#0F172A",
        "text_secondary": "#475569",
        "text_muted": "#94A3B8",
        "text_on_accent": "#FFFFFF",
        "neutral_white": "#FFFFFF",
        "neutral_black": "#000000",
        "tooltip_transparent_mask": "#E532F1",
        "border_subtle": "#E2E8F0",
        "border_strong": "#475569",
        "separator_line": "#E2E8F0",
        "accent_blue": "#2563EB",
        "accent_blue_hover": "#1D4ED8",
        "accent_blue_soft": "#EFF6FF",
        "accent_blue_icon": "#2563EB",
        "success_green": "#22C55E",
        "success_green_deep": "#16A34A",
        "danger_red": "#EF4444",
        "danger_red_deep": "#DC2626",
        "danger_bg": "#FEF2F2",
        "danger_border": "#FCA5A5",
        "sidebar_hover": "#E2E8F0",
        "sidebar_border": "#CBD5E1",
        "sidebar_hover_border": "#CBD5E1",
        "sidebar_text": "#0F172A",
        "modal_overlay": "#64748B",
        "progress_track": "#F1F5F9",
        "progress_border": "#E2E8F0",
        "progress_fill": "#2563EB",
        # Alias conservados para modulos que todavia usan los nombres historicos.
        "bg": "#F8FAFC",
        "surface": "#FFFFFF",
        "footer_bg": "#FFFFFF",
        "border": "#E2E8F0",
        "card_border": "#E2E8F0",
        "text": "#0F172A",
        "text_secondary_legacy": "#475569",
        "left_bar": "#0F172A",
    },
    "dark": {
        "bg_base": "#0F172A",
        "bg_elevated": "#111827",
        "bg_panel": "#111827",
        "bg_card": "#111827",
        "bg_sidebar": "#111827",
        "bg_dialog": "#0F172A",
        "bg_footer": "#111827",
        "surface_alt": "#1E293B",
        "text_primary": "#F8FAFC",
        "text_secondary": "#CBD5E1",
        "text_muted": "#94A3B8",
        "text_on_accent": "#FFFFFF",
        "neutral_white": "#FFFFFF",
        "neutral_black": "#000000",
        "tooltip_transparent_mask": "#E532F1",
        "border_subtle": "#334155",
        "border_strong": "#64748B",
        "separator_line": "#334155",
        "accent_blue": "#2563EB",
        "accent_blue_hover": "#3B82F6",
        "accent_blue_soft": "#172554",
        "accent_blue_icon": "#60A5FA",
        "success_green": "#22C55E",
        "success_green_deep": "#16A34A",
        "danger_red": "#EF4444",
        "danger_red_deep": "#F87171",
        "danger_bg": "#3F1D1D",
        "danger_border": "#7F1D1D",
        "sidebar_hover": "#334155",
        "sidebar_border": "#475569",
        "sidebar_hover_border": "#475569",
        "sidebar_text": "#F8FAFC",
        "modal_overlay": "#94A3B8",
        "progress_track": "#1E293B",
        "progress_border": "#334155",
        "progress_fill": "#3B82F6",
        # Alias conservados para modulos que todavia usan los nombres historicos.
        "bg": "#0F172A",
        "surface": "#111827",
        "footer_bg": "#111827",
        "border": "#334155",
        "card_border": "#334155",
        "text": "#F8FAFC",
        "text_secondary_legacy": "#CBD5E1",
        "left_bar": "#F8FAFC",
    },
}


BUTTON_TOKENS = {
    "blue": {
        "bg": "#2563EB",
        "hover": "#1D4ED8",
        "border": "#1D4ED8",
        "text": "#FFFFFF",
    },
    "green": {
        "bg": "#22C55E",
        "hover": "#16A34A",
        "border": "#16A34A",
        "text": "#FFFFFF",
    },
    "red": {
        "bg": "#EF4444",
        "hover": "#DC2626",
        "border": "#DC2626",
        "text": "#FFFFFF",
    },
    "neutral": {
        "bg": ("#FFFFFF", "#1E293B"),
        "hover": ("#F1F5F9", "#334155"),
        "border": ("#E2E8F0", "#334155"),
        "text": ("#0F172A", "#E2E8F0"),
    },
}


# Tipografia semantica definida por la guia de diseño.
FONT_LABEL = (FONT_FAMILY_PRIMARY, 13, "bold")
FONT_ACTION = (FONT_FAMILY_PRIMARY, 13, "bold")
FONT_CHIP = (FONT_FAMILY_PRIMARY, 12, "bold")
FONT_BODY = (FONT_FAMILY_PRIMARY, 13, "normal")
FONT_BODY_EMPHASIS = (FONT_FAMILY_PRIMARY, 13, "bold")
FONT_AUXILIARY = (FONT_FAMILY_PRIMARY, 11, "normal")
FONT_AUXILIARY_EMPHASIS = (FONT_FAMILY_PRIMARY, 11, "bold")

ACTION_BUTTON_TOKENS = {
    "light": {
        "primary": {
            "bg": "#2563EB",
            "hover": "#1D4ED8",
            "border": "#2563EB",
            "text": "#FFFFFF",
            "icon": "#FFFFFF",
            "chevron": "#DBEAFE",
        },
        "secondary": {
            "bg": "#F1F5F9",
            "hover": "#E2E8F0",
            "border": "#E2E8F0",
            "text": "#0F172A",
            "icon": "#2563EB",
            "chevron": "#64748B",
        },
        "destructive": {
            "bg": "#FEF2F2",
            "hover": "#FEE2E2",
            "border": "#FCA5A5",
            "text": "#DC2626",
            "icon": "#DC2626",
            "chevron": "#EF4444",
        },
    },
    "dark": {
        "primary": {
            "bg": "#2563EB",
            "hover": "#3B82F6",
            "border": "#2563EB",
            "text": "#FFFFFF",
            "icon": "#FFFFFF",
            "chevron": "#DBEAFE",
        },
        "secondary": {
            "bg": "#1E293B",
            "hover": "#334155",
            "border": "#334155",
            "text": "#F8FAFC",
            "icon": "#60A5FA",
            "chevron": "#94A3B8",
        },
        "destructive": {
            "bg": "#3F1D1D",
            "hover": "#5F2121",
            "border": "#7F1D1D",
            "text": "#FCA5A5",
            "icon": "#FCA5A5",
            "chevron": "#F87171",
        },
    },
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
        "light": THEME_TOKENS["light"]["sidebar_hover"],
        "dark": THEME_TOKENS["dark"]["sidebar_hover"],
    },
    "list_item": {
        "selected_bg": THEME_TOKENS["light"]["accent_blue_soft"],
        "normal_bg": "transparent",
    },
}


# =============================================================================

# CONSTANTES DE INTERFAZ DERIVADAS

# =============================================================================


# Dimensiones estandar

BTN_W_MAIN, BTN_H_MAIN = 380, 42

BTN_W_ICON, BTN_H_ICON = 28, 28

SIDEBAR_WIDTH = 28


# Animaciones y transiciones

MAIN_WINDOW_FADE_OUT_STEP = 0.18

MAIN_WINDOW_FADE_OUT_INTERVAL_MS = 12

THEME_SWITCH_SETTLE_MS = 40

DIALOG_ICON_DELAY_MS = 0

DIALOG_PREPARE_DELAY_MS = 55

DIALOG_CENTER_RETRY_DELAY_MS = 52

DIALOG_CENTER_MAX_ATTEMPTS = 5

DIALOG_INITIAL_ALPHA = 0.0

DIALOG_REVEAL_DELAY_MS = 45

DIALOG_REVEAL_OFFSET_Y = 0

DIALOG_REVEAL_STEP_PX = 1

DIALOG_HIDDEN_PARK_OFFSET_PX = 115

DIALOG_FADE_IN_STEP = 0.18

DIALOG_FADE_IN_INTERVAL_MS = 12

DIALOG_FADE_OUT_STEP = 0.18

DIALOG_FADE_OUT_INTERVAL_MS = 12

PROFILE_SWITCH_FADE_DELAY_MS = 90

RESTORE_FADE_DELAY_MS = 90


# Tipografia

FONT_SIZE_XS = 11

FONT_SIZE_SM = 12

FONT_SIZE_MD = 13

FONT_SIZE_BASE = 13

FONT_SIZE_LG = 13

FONT_SIZE_XL = 14


# Metricas compartidas

BORDER_WIDTH_THIN = 1

BORDER_WIDTH_MEDIUM = 1

CORNER_RADIUS_SM = 8

CORNER_RADIUS_MD = 10

CORNER_RADIUS_LG = 12

CORNER_RADIUS_XL = 12

CORNER_RADIUS_2XL = 12

PADDING_XS = 4

PADDING_SM = 6

PADDING_MD = 8

PADDING_LG = 10

PADDING_XL = 12

PADDING_2XL = 14

PADDING_3XL = 16

PADDING_4XL = 20

PADDING_5XL = 24


# Ventana principal

MAIN_WINDOW_WIDTH = 750

MAIN_WINDOW_HEIGHT = 460


MAIN_WINDOW_SIDE_PADX = 20

MAIN_WINDOW_LEFT_PADY = (8, 8)

MAIN_WINDOW_RIGHT_PADY = (8, 8)

MAIN_WINDOW_CENTER_PADY = (8, 8)

MAIN_WINDOW_HEADER_PADY = (4, 8)

MAIN_WINDOW_GREETING_FONT_SIZE = 16

MAIN_WINDOW_GREETING_MIN_FONT_SIZE = 14

MAIN_WINDOW_SUBTITLE_FONT_SIZE = 13

MAIN_WINDOW_SUBTITLE_MIN_FONT_SIZE = 11

MAIN_WINDOW_HEADER_MIN_HEIGHT = 72

MAIN_WINDOW_HEADER_CONTENT_GAP = 10

MAIN_WINDOW_HEADER_LINE_HEIGHT = 1

MAIN_WINDOW_HEADER_TOP_INSET = 4

MAIN_WINDOW_HEADER_LOGO_TEXT_GAP = 6

MAIN_WINDOW_HEADER_TEXT_SIDE_PAD = 20
MAIN_WINDOW_HEADER_TEXT_WIDTH = 430

MAIN_WINDOW_HEADER_TEXT_GAP = 1

MAIN_WINDOW_HEADER_BOTTOM_INSET = 5

MAIN_WINDOW_MAIN_MENU_RADIUS = CORNER_RADIUS_LG

MAIN_WINDOW_MAIN_MENU_BORDER_WIDTH = BORDER_WIDTH_THIN

MAIN_WINDOW_MAIN_MENU_PAD = 14

MAIN_WINDOW_MAIN_MENU_BOTTOM_GAP = 16

MAIN_WINDOW_BUTTON_FONT_SIZE = 13

MAIN_WINDOW_BUTTON_MIN_FONT_SIZE = 11

MAIN_WINDOW_BUTTON_MIN_WIDTH = 250
MAIN_WINDOW_RIGHT_ACTION_WIDTH = 250

MAIN_WINDOW_BUTTON_BORDER_WIDTH = BORDER_WIDTH_MEDIUM

MAIN_WINDOW_CARD_BORDER_WIDTH = BORDER_WIDTH_THIN
MAIN_WINDOW_ACTION_BORDER_WIDTH = BORDER_WIDTH_THIN

MAIN_WINDOW_BUTTON_SPACING = 4

MAIN_WINDOW_STATUS_AREA_PADY = (0, 0)

MAIN_WINDOW_STATUS_MIN_VISIBLE_SECONDS = 1.0

MAIN_WINDOW_FOOTER_HEIGHT = 34

MAIN_WINDOW_FOOTER_LINE_HEIGHT = 1

MAIN_WINDOW_FOOTER_FONT_SIZE = 11

MAIN_WINDOW_MODAL_FAIL_SAFE_DELAY_MS = 900

MAIN_WINDOW_MODAL_OVERLAY_ALPHA = 0.18


# Controles compartidos de dialogos

MESSAGE_AUTO_CLOSE_SECONDS = 10

DIALOG_SECONDARY_ICON_DELAY_MS = 220

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

MESSAGE_DIALOG_WIDTH = 390
MESSAGE_DIALOG_HEIGHT = 230
MESSAGE_DIALOG_ICON_SIZE = (26, 26)
MESSAGE_DIALOG_ICON_BADGE_SIZE = 44
MESSAGE_DIALOG_TEXT_WRAP = 320

MESSAGE_DIALOG_TEXT_FONT_SIZE = FONT_SIZE_BASE

MESSAGE_DIALOG_TEXT_PADX = 20

MESSAGE_DIALOG_TEXT_PADY = (8, 18)

MESSAGE_DIALOG_OK_WIDTH = 120

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

SETTINGS_DIALOG_FORMAT_SHELL_RADIUS = CORNER_RADIUS_MD

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

STATUS_PANEL_CORNER_RADIUS = CORNER_RADIUS_LG

STATUS_PANEL_BORDER_WIDTH = BORDER_WIDTH_THIN

STATUS_PANEL_PADX = 0

STATUS_PANEL_PADY = (0, 0)

STATUS_PANEL_ROW_PADX = 16

STATUS_PANEL_TOP_ROW_PADY = (12, 6)

STATUS_PANEL_STATUS_FONT_SIZE = 13

STATUS_PANEL_PERCENT_FONT_SIZE = 11

STATUS_PANEL_PERCENT_PADX = (0, 8)

STATUS_PANEL_CANCEL_SIZE = 24

STATUS_PANEL_CANCEL_RADIUS = CORNER_RADIUS_SM

STATUS_PANEL_CANCEL_FONT_SIZE = 12

STATUS_PANEL_PROGRESS_HEIGHT = 8

STATUS_PANEL_PROGRESS_RADIUS = 4

STATUS_PANEL_PROGRESS_PADY = (0, 6)

STATUS_PANEL_FILE_ROW_PADY = (0, 12)

STATUS_PANEL_FILE_PREFIX_FONT_SIZE = 10

STATUS_PANEL_FILE_TEXT_FONT_SIZE = 10

STATUS_PANEL_FILE_WRAP_DEFAULT = 460

STATUS_PANEL_MIN_USABLE_WIDTH = 180

STATUS_PANEL_PREFIX_GAP = 6

STATUS_PANEL_MIN_WRAP = 160

STATUS_PANEL_DOTS_INTERVAL_MS = 450

STATUS_PANEL_PROGRESS_TICK_MS = 16

STATUS_PANEL_SUCCESS_RESET_DELAY_MS = 900

STATUS_PANEL_ELLIPSIS_MAX_LEN = 72

STATUS_PANEL_CONTEXT_MAX_LEN = 120
STATUS_PANEL_DETAILS_HEIGHT = 0


# Tags dialog

TAGS_DIALOG_WIDTH = 640

TAGS_DIALOG_HEIGHT = 650

TAGS_DIALOG_SINGLE_HEIGHT = 480

TAGS_DIALOG_SECTION_MIN_HEIGHT = 150

TAGS_DIALOG_SINGLE_SECTION_MIN_HEIGHT = 260

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

TAGS_DIALOG_AUTODETECT_BUTTON_WIDTH = 104

TAGS_DIALOG_AUTODETECT_BUTTON_HEIGHT = 28

TAGS_DIALOG_AUTODETECT_BUTTON_PADX = (8, 0)

TAGS_DIALOG_ROW_PADY = (0, 5)

TAGS_DIALOG_PILL_SPACING = 6

TAGS_DIALOG_WRAP_SAFETY_PX = 2

TAGS_DIALOG_PILL_WIDTH_SAFETY_PX = 2

TAGS_DIALOG_PILL_RADIUS = CORNER_RADIUS_LG

TAGS_DIALOG_PILL_LABEL_PADX = (10, 4)

TAGS_DIALOG_PILL_LABEL_PADY = 2

TAGS_DIALOG_PILL_CLOSE_SIZE = 22

TAGS_DIALOG_PILL_CLOSE_RADIUS = CORNER_RADIUS_SM

TAGS_DIALOG_PILL_CLOSE_PADX = (0, 8)

TAGS_DIALOG_PILL_CLOSE_PADY = 3


# Tooltip

TOOLTIP_FRAME_CORNER_RADIUS = CORNER_RADIUS_MD

TOOLTIP_FRAME_BORDER_WIDTH = BORDER_WIDTH_THIN

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

SIDEBAR_ICON_SIZE = (18, 18)

THEME_TOGGLE_ICON_SIZE = (18, 18)
ACTION_ICON_SIZE = (18, 18)

LOGO_TARGET_WIDTH = 92


# Sidebars

LEFT_SIDEBAR_HEIGHT = 370

LEFT_SIDEBAR_FONT_SIZE = FONT_SIZE_BASE

PILL_TEXT_BUTTON_FONT_SIZE = FONT_SIZE_MD


RIGHT_SIDEBAR_BUTTON_SPACING = 0

RIGHT_SIDEBAR_BUTTON_BORDER_WIDTH = 0


# Progress bar


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
    (0.0, THEME_TOKENS["light"]["progress_fill"]),
    (1.0, THEME_TOKENS["light"]["progress_fill"]),
]


def resolve_theme_name(theme_name: str | None) -> str:

    if isinstance(theme_name, str) and theme_name.lower() == "dark":
        return "dark"

    return "light"


def get_theme_tokens(theme_name: str | None) -> dict:

    return THEME_TOKENS[resolve_theme_name(theme_name)]


def get_button_tokens(button_name: str = "blue") -> dict:

    return BUTTON_TOKENS.get(button_name, BUTTON_TOKENS["blue"])


def get_action_button_tokens(theme_name: str | None, variant: str = "primary") -> dict:

    theme_key = resolve_theme_name(theme_name)

    return ACTION_BUTTON_TOKENS[theme_key].get(variant, ACTION_BUTTON_TOKENS[theme_key]["primary"])


def get_color_pair(token_name: str) -> tuple[str, str]:

    return THEME_TOKENS["light"][token_name], THEME_TOKENS["dark"][token_name]


def hex_to_rgb(value: str) -> tuple[int, int, int]:

    value = (value or "").strip().lstrip("#")

    if len(value) != 6:
        return 0, 0, 0

    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:

    return "#{:02X}{:02X}{:02X}".format(*rgb)


def mix_color(color_a: str, color_b: str, ratio: float) -> str:

    ratio = max(0.0, min(1.0, float(ratio)))

    ar, ag, ab = hex_to_rgb(color_a)

    br, bg, bb = hex_to_rgb(color_b)

    return rgb_to_hex(
        (
            int(ar + (br - ar) * ratio),
            int(ag + (bg - ag) * ratio),
            int(ab + (bb - ab) * ratio),
        )
    )


def with_alpha(color: str, alpha: int) -> tuple[int, int, int, int]:

    r, g, b = hex_to_rgb(color)

    return r, g, b, max(0, min(255, int(alpha)))