from __future__ import annotations

import os
from typing import Dict, List, Tuple

import customtkinter as ctk
from PIL import Image

from utils.path_utils import resource_path


def load_dual_icon(light_name: str, dark_name: str, size: Tuple[int, int]) -> ctk.CTkImage | None:
    try:
        light_img = Image.open(resource_path(light_name))
        dark_img = Image.open(resource_path(dark_name))
        return ctk.CTkImage(light_image=light_img, dark_image=dark_img, size=size)
    except Exception as e:
        print(f"Error cargando iconos {light_name}/{dark_name}: {e}")
        return None


def load_single_icon(name: str, size: Tuple[int, int]) -> ctk.CTkImage | None:
    try:
        img = Image.open(resource_path(name))
        return ctk.CTkImage(img, size=size)
    except Exception as e:
        print(f"Error cargando icono {name}: {e}")
        return None


def load_icon_set(keys: Tuple[str, ...], size=(22, 22)) -> Dict[str, ctk.CTkImage | None]:
    icons: Dict[str, ctk.CTkImage | None] = {}
    for key in keys:
        try:
            img_for_dark_theme = Image.open(resource_path(f"{key}_oscuro.png"))
            img_for_light_theme = Image.open(resource_path(f"{key}_claro.png"))
            icons[key] = ctk.CTkImage(
                light_image=img_for_light_theme,
                dark_image=img_for_dark_theme,
                size=size,
            )
        except Exception as e:
            print(f"Error cargando icono '{key}': {e}")
            icons[key] = None
    return icons


def load_gif_frames(gif_name: str, max_width: int, max_height: int) -> Tuple[List[Image.Image], int]:
    frames: List[Image.Image] = []
    delay = 100
    if max_width <= 0 or max_height <= 0:
        return frames, delay
    try:
        gif_path = resource_path(gif_name)
        with Image.open(gif_path) as im:
            delay = im.info.get("duration", 100)
            original_width, original_height = im.size
            if original_height <= 0 or original_width <= 0:
                return frames, delay
            ratio = min(max_width / original_width, max_height / original_height)
            target_width, target_height = int(original_width * ratio), int(original_height * ratio)
            gif_size = (target_width, target_height)
            for i in range(im.n_frames):
                im.seek(i)
                frame_rgba = im.convert("RGBA")
                resized_frame = frame_rgba.resize(gif_size, Image.Resampling.LANCZOS)
                frames.append(resized_frame)
    except Exception as e:
        print(f"Error al cargar o redimensionar el GIF {gif_name}: {e}")
    return frames, delay
