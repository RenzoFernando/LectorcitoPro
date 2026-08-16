import os
import sys
import customtkinter as ctk
from PIL import Image, ImageTk, ImageOps
from utils import resource_path
from view.ui_constants import SIDEBAR_ICON_SIZE, THEME_TOGGLE_ICON_SIZE, LOGO_TARGET_WIDTH
from app_logging import log_warning

# =============================================================================
# GESTION DE RECURSOS VISUALES
# =============================================================================

def get_app_icon_path() -> str:
    return resource_path(os.path.join("branding", "lector.ico"))


def get_app_icon_png_path() -> str:
    return resource_path(os.path.join("branding", "lector.png"))


def load_sidebar_icons(size=SIDEBAR_ICON_SIZE) -> dict:
    icons = {}
    icon_keys = ["ver", "nover", "etiqueta", "traducir", "restaurar", "perfil", "github", "info", "ajustes"]

    for key in icon_keys:
        try:
            img_dark = Image.open(resource_path(os.path.join("icons", f"{key}_oscuro.png")))
            img_light = Image.open(resource_path(os.path.join("icons", f"{key}_claro.png")))
            icons[key] = ctk.CTkImage(light_image=img_dark, dark_image=img_light, size=size)
        except Exception as e:
            log_warning(str(e), operation="load_sidebar_icon", file_path=key)
            icons[key] = None

    try:
        sun_image = Image.open(resource_path(os.path.join("icons", "sol.png"))).convert("RGBA")
        moon_image = Image.open(resource_path(os.path.join("icons", "luna.png"))).convert("RGBA")

        sun_rgb = Image.merge("RGB", sun_image.split()[:3])
        moon_rgb = Image.merge("RGB", moon_image.split()[:3])
        sun_inverse = ImageOps.invert(sun_rgb).convert("RGBA")
        moon_inverse = ImageOps.invert(moon_rgb).convert("RGBA")
        sun_inverse.putalpha(sun_image.getchannel("A"))
        moon_inverse.putalpha(moon_image.getchannel("A"))

        icons["sun"] = ctk.CTkImage(light_image=sun_image, dark_image=sun_inverse, size=THEME_TOGGLE_ICON_SIZE)
        icons["moon"] = ctk.CTkImage(light_image=moon_inverse, dark_image=moon_image, size=THEME_TOGGLE_ICON_SIZE)
    except Exception as e:
        log_warning(str(e), operation="load_theme_icons")
        icons["sun"] = None
        icons["moon"] = None

    return icons


def load_logo(target_width=LOGO_TARGET_WIDTH) -> ctk.CTkImage | None:
    try:
        logo_light = Image.open(resource_path(os.path.join("branding", "logo_oscuro.png")))
        logo_dark = Image.open(resource_path(os.path.join("branding", "logo_claro.png")))

        ow, oh = logo_light.size
        ratio = oh / ow if ow else 1.0
        target_height = int(target_width * ratio)

        return ctk.CTkImage(
            light_image=logo_light, dark_image=logo_dark, size=(target_width, target_height)
        )
    except Exception as e:
        log_warning(str(e), operation="load_logo")
        return None


def safe_set_window_icon(window) -> None:
    if sys.platform.startswith("win"):
        icon_path = get_app_icon_path()
        if icon_path and os.path.exists(icon_path):
            try:
                window.iconbitmap(icon_path)
                window._icon_path = icon_path
            except Exception as e:
                log_warning(str(e), operation="set_window_icon", file_path=icon_path)
        return

    icon_path = get_app_icon_png_path()
    if icon_path and os.path.exists(icon_path):
        try:
            icon_image = ImageTk.PhotoImage(Image.open(icon_path))
            window.iconphoto(True, icon_image)
            window._icon_photo = icon_image
            window._icon_path = icon_path
        except Exception as e:
            log_warning(str(e), operation="set_window_icon", file_path=icon_path)
