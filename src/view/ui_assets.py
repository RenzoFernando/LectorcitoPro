import os
import customtkinter as ctk
from PIL import Image
from utils import resource_path

# =============================================================================
# GESTION DE RECURSOS VISUALES
# =============================================================================

def get_app_icon_path() -> str:
    return resource_path(os.path.join("branding", "lector.ico"))


def load_sidebar_icons(size=(30, 30)) -> dict:
    icons = {}
    icon_keys = ["ver", "nover", "etiqueta", "traducir", "restaurar", "perfil", "github", "info", "ajustes"]

    for key in icon_keys:
        try:
            img_dark = Image.open(resource_path(os.path.join("icons", f"{key}_oscuro.png")))
            img_light = Image.open(resource_path(os.path.join("icons", f"{key}_claro.png")))
            icons[key] = ctk.CTkImage(light_image=img_light, dark_image=img_dark, size=size)
        except Exception as e:
            print(f"Error cargando icono '{key}': {e}")
            icons[key] = None

    try:
        icons["sun"] = ctk.CTkImage(Image.open(resource_path(os.path.join("icons", "sol.png"))), size=(32, 32))
        icons["moon"] = ctk.CTkImage(Image.open(resource_path(os.path.join("icons", "luna.png"))), size=(32, 32))
    except Exception as e:
        print(f"Error cargando iconos de tema: {e}")
        icons["sun"] = None
        icons["moon"] = None

    return icons


def load_logo(target_width=150) -> ctk.CTkImage | None:
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
        print(f"Error al cargar logo: {e}")
        return None


def safe_set_window_icon(window) -> None:
    icon_path = get_app_icon_path()
    if icon_path and os.path.exists(icon_path):
        try:
            window.iconbitmap(icon_path)
            window._icon_path = icon_path
        except Exception as e:
            print(f"Error al asignar icono: {e}")

