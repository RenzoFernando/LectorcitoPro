import os
import sys

import customtkinter as ctk
from PIL import Image, ImageTk

from app_logging import log_warning
from utils import resource_path
from view.svg_icons import load_ctk_svg_image
from view.ui_constants import (
    ACTION_ICON_SIZE,
    LOGO_TARGET_WIDTH,
    SIDEBAR_ICON_SIZE,
    THEME_TOGGLE_ICON_SIZE,
    get_theme_tokens,
)

# =============================================================================
# GESTION DE RECURSOS VISUALES
# =============================================================================


def get_app_icon_path() -> str:
    return resource_path(os.path.join("branding", "app_icon.ico"))


def get_app_icon_png_path() -> str:
    return resource_path(os.path.join("branding", "app_icon.png"))


def _svg_icon_path(name: str) -> str:
    return resource_path(os.path.join("icons", f"{name}.svg"))


def _load_svg_icon(
    name: str,
    *,
    size: tuple[int, int],
    light_color: str,
    dark_color: str,
) -> ctk.CTkImage | None:
    path = _svg_icon_path(name)
    if not os.path.exists(path):
        log_warning("SVG no encontrado.", operation="load_svg_icon", file_path=path)
        return None
    try:
        return load_ctk_svg_image(
            path,
            size=size,
            light_color=light_color,
            dark_color=dark_color,
        )
    except Exception as error:
        log_warning(str(error), operation="load_svg_icon", file_path=path)
        return None


def load_sidebar_icons(size=SIDEBAR_ICON_SIZE) -> dict:
    """Carga la barra superior desde los SVG vectoriales del proyecto."""
    light = get_theme_tokens("Light")
    dark = get_theme_tokens("Dark")
    toolbar_light = light["accent_blue"]
    toolbar_dark = dark["accent_blue_icon"]

    icon_names = {
        "ver": "view",
        "nover": "hide",
        "etiqueta": "media",
        "traducir": "language",
        "restaurar": "restore",
        "perfil": "profiles",
        "github": "github",
        "info": "info",
        "ajustes": "settings",
        "sun": "sun",
        "moon": "moon",
    }

    icons = {}
    for key, svg_name in icon_names.items():
        icon_size = THEME_TOGGLE_ICON_SIZE if key in {"sun", "moon"} else size
        icons[key] = _load_svg_icon(
            svg_name,
            size=icon_size,
            light_color=toolbar_light,
            dark_color=toolbar_dark,
        )
    return icons


def load_action_icons(size=ACTION_ICON_SIZE) -> dict:
    """Carga las acciones principales desde una unica fuente SVG por icono."""
    light = get_theme_tokens("Light")
    dark = get_theme_tokens("Dark")
    icon_names = {
        "choose": "read_complete",
        "openlect": "readings_folder",
        "create_tree": "tree",
        "openlast": "last_report",
        "selpath": "destination",
        "delete": "delete",
    }
    colors = {
        "choose": ("#FFFFFF", "#FFFFFF"),
        "openlect": ("#FFFFFF", "#FFFFFF"),
        "create_tree": (light["accent_blue"], dark["accent_blue_icon"]),
        "openlast": (light["accent_blue"], dark["accent_blue_icon"]),
        "selpath": (light["accent_blue"], dark["accent_blue_icon"]),
        "delete": (light["danger_red_deep"], dark["danger_red_deep"]),
    }

    icons = {}
    for key, svg_name in icon_names.items():
        light_color, dark_color = colors[key]
        icons[key] = _load_svg_icon(
            svg_name,
            size=size,
            light_color=light_color,
            dark_color=dark_color,
        )
    return icons


def load_disabled_sidebar_icons(size=SIDEBAR_ICON_SIZE) -> dict:
    """Carga iconos neutros para el estado modal deshabilitado."""
    light = get_theme_tokens("Light")
    dark = get_theme_tokens("Dark")
    icon_names = {
        "ver": "view",
        "nover": "hide",
        "etiqueta": "media",
        "traducir": "language",
        "restaurar": "restore",
        "perfil": "profiles",
        "github": "github",
        "info": "info",
        "ajustes": "settings",
        "sun": "sun",
        "moon": "moon",
    }

    icons = {}
    for key, svg_name in icon_names.items():
        icon_size = THEME_TOGGLE_ICON_SIZE if key in {"sun", "moon"} else size
        icons[key] = _load_svg_icon(
            svg_name,
            size=icon_size,
            light_color=light["text_primary"],
            dark_color=dark["text_primary"],
        )
    return icons


def load_disabled_action_icons(size=ACTION_ICON_SIZE) -> dict:
    """Carga las acciones principales sin color semantico durante un modal."""
    light = get_theme_tokens("Light")
    dark = get_theme_tokens("Dark")
    icon_names = {
        "choose": "read_complete",
        "openlect": "readings_folder",
        "create_tree": "tree",
        "openlast": "last_report",
        "selpath": "destination",
        "delete": "delete",
    }

    return {
        key: _load_svg_icon(
            svg_name,
            size=size,
            light_color=light["text_primary"],
            dark_color=dark["text_primary"],
        )
        for key, svg_name in icon_names.items()
    }


def load_add_icon(
    size=(14, 14),
    *,
    light_color: str = "#FFFFFF",
    dark_color: str = "#FFFFFF",
) -> ctk.CTkImage | None:
    return _load_svg_icon(
        "add",
        size=size,
        light_color=light_color,
        dark_color=dark_color,
    )


def load_delete_icon(
    size=(14, 14),
    *,
    light_color: str | None = None,
    dark_color: str | None = None,
) -> ctk.CTkImage | None:
    light = get_theme_tokens("Light")
    dark = get_theme_tokens("Dark")
    return _load_svg_icon(
        "delete",
        size=size,
        light_color=light_color or light["danger_red_deep"],
        dark_color=dark_color or dark["danger_red_deep"],
    )


def load_close_icon(
    size=(14, 14),
    *,
    light_color: str | None = None,
    dark_color: str | None = None,
) -> ctk.CTkImage | None:
    light = get_theme_tokens("Light")
    dark = get_theme_tokens("Dark")
    return _load_svg_icon(
        "close",
        size=size,
        light_color=light_color or light["accent_blue"],
        dark_color=dark_color or dark["accent_blue_icon"],
    )


def load_cancel_reading_icon(
    size=(14, 14),
    *,
    light_color: str | None = None,
    dark_color: str | None = None,
) -> ctk.CTkImage | None:
    light = get_theme_tokens("Light")
    dark = get_theme_tokens("Dark")
    return _load_svg_icon(
        "cancel_reading",
        size=size,
        light_color=light_color or light["danger_red_deep"],
        dark_color=dark_color or dark["danger_red_deep"],
    )


def load_chevron_icon(
    size=(14, 14),
    *,
    light_color: str | None = None,
    dark_color: str | None = None,
) -> ctk.CTkImage | None:
    light = get_theme_tokens("Light")
    dark = get_theme_tokens("Dark")
    return _load_svg_icon(
        "chevron_right",
        size=size,
        light_color=light_color or light["accent_blue"],
        dark_color=dark_color or dark["accent_blue_icon"],
    )


def load_status_dot_icon(
    size=(10, 10),
    *,
    light_color: str | None = None,
    dark_color: str | None = None,
) -> ctk.CTkImage | None:
    light = get_theme_tokens("Light")
    dark = get_theme_tokens("Dark")
    return _load_svg_icon(
        "status_dot",
        size=size,
        light_color=light_color or light["text_muted"],
        dark_color=dark_color or dark["text_muted"],
    )


def load_checkmark_icon(
    size=(14, 14),
    *,
    light_color: str | None = None,
    dark_color: str | None = None,
) -> ctk.CTkImage | None:
    return _load_svg_icon(
        "checkmark",
        size=size,
        light_color=light_color or "#FFFFFF",
        dark_color=dark_color or "#FFFFFF",
    )


def load_info_icon(size=(24, 24)) -> ctk.CTkImage | None:
    light = get_theme_tokens("Light")
    dark = get_theme_tokens("Dark")
    return _load_svg_icon(
        "info",
        size=size,
        light_color=light["accent_blue"],
        dark_color=dark["accent_blue_icon"],
    )


def load_logo(target_width=LOGO_TARGET_WIDTH) -> ctk.CTkImage | None:
    try:
        logo_light = Image.open(resource_path(os.path.join("branding", "logo_light_theme.png")))
        logo_dark = Image.open(resource_path(os.path.join("branding", "logo_dark_theme.png")))

        ow, oh = logo_light.size
        ratio = oh / ow if ow else 1.0
        target_height = int(target_width * ratio)

        return ctk.CTkImage(
            light_image=logo_light,
            dark_image=logo_dark,
            size=(target_width, target_height),
        )
    except Exception as error:
        log_warning(str(error), operation="load_logo")
        return None


def safe_set_window_icon(window) -> None:
    if sys.platform.startswith("win"):
        icon_path = get_app_icon_path()
        if icon_path and os.path.exists(icon_path):
            try:
                window.iconbitmap(icon_path)
                window._icon_path = icon_path
            except Exception as error:
                log_warning(str(error), operation="set_window_icon", file_path=icon_path)
        return

    icon_path = get_app_icon_png_path()
    if icon_path and os.path.exists(icon_path):
        try:
            icon_image = ImageTk.PhotoImage(Image.open(icon_path))
            window.iconphoto(True, icon_image)
            window._icon_photo = icon_image
            window._icon_path = icon_path
        except Exception as error:
            log_warning(str(error), operation="set_window_icon", file_path=icon_path)
