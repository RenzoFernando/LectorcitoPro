from __future__ import annotations

import customtkinter as ctk
import tkinter as tk
import datetime
import os
import random
import webbrowser

from PIL import Image, ImageDraw, ImageFilter, ImageTk, ImageStat
from utils import resource_path

from app_meta import APP_DISPLAY_NAME, APP_WEBSITE_URL
from view.translations import TRANSLATIONS, translate_default
from view.dialogs import MessageDialog, _get_widget_window_rect, _get_widget_workarea, _get_centered_position
from view.tooltip import CustomTooltip
from view.ui_constants import *

from view.ui_constants import (
    FONT_FAMILY_PRIMARY,
    VERSION, YEAR, AUTHOR, REPO_URL,
    COLORS, BTN_W_MAIN, BTN_H_MAIN,
    get_theme_tokens, get_button_tokens, hex_to_rgb, with_alpha,
    MAIN_WINDOW_SHOW_DELAY_MS, MAIN_WINDOW_CENTER_RETRY_DELAY_MS, MAIN_WINDOW_CENTER_MAX_ATTEMPTS,
    MAIN_WINDOW_INITIAL_ALPHA, MAIN_WINDOW_REVEAL_DELAY_MS, MAIN_WINDOW_REVEAL_OFFSET_Y, MAIN_WINDOW_REVEAL_STEP_PX,
    MAIN_WINDOW_HIDDEN_PARK_OFFSET_PX, MAIN_WINDOW_FADE_IN_STEP, MAIN_WINDOW_FADE_IN_INTERVAL_MS, MAIN_WINDOW_FADE_OUT_STEP, MAIN_WINDOW_FADE_OUT_INTERVAL_MS,
    MAIN_WINDOW_SOFT_REFRESH_ALPHA, MAIN_WINDOW_SWITCH_FADE_OUT_STEP, MAIN_WINDOW_SWITCH_FADE_OUT_INTERVAL_MS,
    MAIN_WINDOW_SWITCH_HOLD_MS, MAIN_WINDOW_SWITCH_REBUILD_DELAY_MS, MAIN_WINDOW_SWITCH_FADE_IN_STEP, MAIN_WINDOW_SWITCH_FADE_IN_INTERVAL_MS
)
from view.ui_assets import load_sidebar_icons, load_logo, safe_set_window_icon
from view.sidebars import LeftSidebar, RightSidebar, PillTextButton, BlendedRoundedFrame
from view.status_panel import StatusPanel
from view.profiles_dialog import ProfilesDialog
from view.settings_dialog import SettingsDialog
from view.tags_dialog import TagsConfigDialog


# =============================================================================
# INTERFAZ PRINCIPAL (MAIN WINDOW)
# =============================================================================

class LectorcitoApp(ctk.CTk):

    def __init__(self, cfg: dict, controller):
        super().__init__()

        self.withdraw()
        self.attributes("-alpha", 0.0)

        self.TRANSLATIONS = TRANSLATIONS
        self.config = cfg
        self.controller = controller
        self.lang = self.config.get("language", "es")
        self.current_theme = self.config.get("theme", "Light")
        self.config["language"] = self.lang
        self.config["theme"] = self.current_theme

        self.REPO_URL = REPO_URL
        self.tooltips: dict[str, CustomTooltip] = {}
        self._is_modal_open = False
        self._modal_fail_safe_after_id = None
        self._dialog_cache = {}
        self._reveal_target_y = None
        self._is_theme_switching = False
        self._is_profile_switching = False
        self._profile_switch_apply_callback = None
        self._profile_switch_complete_callback = None
        self._background_after_id = None
        self._background_photo = None
        self._background_image = None
        self._background_cache_key = None
        self._background_revision = 0
        self._surface_backdrops = {}

        self.title(APP_DISPLAY_NAME)
        self._app_w = MAIN_WINDOW_WIDTH
        self._app_h = MAIN_WINDOW_HEIGHT
        self.geometry(f"{self._app_w}x{self._app_h}")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._close_with_fade_out)

        safe_set_window_icon(self)

        self.icons = load_sidebar_icons()
        self.logo_image = load_logo()
        self._header_logo_assets = self._load_header_logo_assets()
        self._header_logo_photo = None
        self._header_backdrop_photo = None
        self._header_greeting_text = ""
        self._header_refresh_after_id = None
        self._header_logo_render_cache = {}

        self._build_ui()
        self.update_ui_texts()
        self.apply_theme()
        self.toggle_ui_for_processing(is_active=False)

        self.after(MAIN_WINDOW_SHOW_DELAY_MS, self._precise_center_and_show)
        self.after(MAIN_WINDOW_SHOW_DELAY_MS + MAIN_WINDOW_PRELOAD_DIALOGS_EXTRA_DELAY_MS, self._preload_persistent_dialogs)

    def _load_header_logo_assets(self):
        try:
            return {
                "light": Image.open(resource_path(os.path.join("branding", "logo_oscuro.png"))).convert("RGBA"),
                "dark": Image.open(resource_path(os.path.join("branding", "logo_claro.png"))).convert("RGBA")
            }
        except Exception:
            return {"light": None, "dark": None}

    def _get_header_scaling(self) -> float:
        for attr in ("_get_window_scaling", "_get_widget_scaling"):
            getter = getattr(self, attr, None)
            if callable(getter):
                try:
                    scale = float(getter())
                    if scale > 0:
                        return scale
                except Exception:
                    pass
        return 1.0

    def _get_header_logo_image(self):
        base_logo = self._header_logo_assets.get("light" if self.current_theme == "Light" else "dark")
        if base_logo is None:
            return None

        scale = max(1.0, self._get_header_scaling())
        target_width = max(1, int(round(LOGO_TARGET_WIDTH * scale)))
        cache_key = ("light" if self.current_theme == "Light" else "dark", target_width)
        cached = self._header_logo_render_cache.get(cache_key)
        if cached is not None:
            return cached

        ow, oh = base_logo.size
        ratio = oh / ow if ow else 1.0
        target_height = max(1, int(round(target_width * ratio)))
        resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.LANCZOS)
        rendered = base_logo.resize((target_width, target_height), resample)
        self._header_logo_render_cache[cache_key] = rendered
        return rendered

    def _schedule_header_refresh(self, event=None):
        if event is not None and getattr(event, "widget", None) not in (getattr(self, "header_frame", None), getattr(self, "header_canvas", None)):
            return
        if self._header_refresh_after_id is not None:
            try:
                self.after_cancel(self._header_refresh_after_id)
            except Exception:
                pass
        try:
            self._header_refresh_after_id = self.after(max(1, int(MAIN_WINDOW_BG_REFRESH_DELAY_MS)), self._refresh_header_canvas)
        except Exception:
            self._header_refresh_after_id = None

    def _refresh_header_canvas(self):
        self._header_refresh_after_id = None
        if not hasattr(self, "header_canvas") or not self.header_canvas.winfo_exists():
            return

        try:
            w = max(1, int(self.header_canvas.winfo_width()))
            h = max(1, int(self.header_canvas.winfo_height()))
        except Exception:
            return

        theme = get_theme_tokens(self.current_theme)
        patch, _ = self.get_backdrop_patch(self.header_canvas, width=w, height=h)
        if patch is None:
            patch = Image.new("RGBA", (w, h), with_alpha(theme["bg_base"], 255))

        self._header_backdrop_photo = ImageTk.PhotoImage(patch)
        self.header_canvas.delete("all")
        self.header_canvas.create_image(0, 0, image=self._header_backdrop_photo, anchor="nw")

        logo = self._get_header_logo_image()
        current_y = 0
        if logo is not None:
            self._header_logo_photo = ImageTk.PhotoImage(logo)
            top_y = max(0, 4)
            self.header_canvas.create_image(w / 2, top_y, image=self._header_logo_photo, anchor="n")
            current_y = top_y + logo.height + 8
        else:
            self._header_logo_photo = None
            current_y = max(0, 4)

        self.header_canvas.create_text(
            w / 2,
            current_y,
            text=self._header_greeting_text,
            anchor="n",
            font=(FONT_FAMILY_PRIMARY, max(1, int(round(MAIN_WINDOW_GREETING_FONT_SIZE * 0.92)))),
            fill=theme["text_primary"],
            justify="center"
        )

    def get_real_window_rect(self):
        return _get_widget_window_rect(self)

    def _get_hidden_window_position(self, target_rect):
        left, top, right, bottom = target_rect
        area_h = max(1, int(bottom - top))
        x = int(right + MAIN_WINDOW_HIDDEN_PARK_OFFSET_PX)
        y = int(top + max(0, (area_h - int(self._app_h)) / 2))
        return x, y

    def _precise_center_and_show(self):
        try:
            self.update_idletasks()
            self._startup_target_rect = _get_widget_workarea(self)
            hidden_x, hidden_y = self._get_hidden_window_position(self._startup_target_rect)
            self.geometry(f"{self._app_w}x{self._app_h}+{hidden_x}+{hidden_y}")

            self.attributes("-alpha", 0.0)
            self.deiconify()
            self.after(MAIN_WINDOW_CENTER_RETRY_DELAY_MS, lambda: self._stabilize_initial_position(1))

        except Exception:
            self.deiconify()
            self.attributes("-alpha", 1.0)

    def _stabilize_initial_position(self, attempt=1):
        try:
            target_rect = getattr(self, "_startup_target_rect", _get_widget_workarea(self))
            target_cx = int((target_rect[0] + target_rect[2]) / 2)
            target_cy = int((target_rect[1] + target_rect[3]) / 2)
            actual_rect = self.get_real_window_rect()
            actual_cx = int((actual_rect[0] + actual_rect[2]) / 2)
            actual_cy = int((actual_rect[1] + actual_rect[3]) / 2)
            dx = target_cx - actual_cx
            dy = target_cy - actual_cy

            if (abs(dx) > 1 or abs(dy) > 1) and attempt < MAIN_WINDOW_CENTER_MAX_ATTEMPTS:
                self.geometry(f"{self._app_w}x{self._app_h}+{int(self.winfo_x()) + dx}+{int(self.winfo_y()) + dy}")
                self.after(MAIN_WINDOW_CENTER_RETRY_DELAY_MS, lambda: self._stabilize_initial_position(attempt + 1))
                return

            self._reveal_target_y = int(self.winfo_y())
            if MAIN_WINDOW_REVEAL_OFFSET_Y > 0:
                self.geometry(f"{self._app_w}x{self._app_h}+{int(self.winfo_x())}+{self._reveal_target_y + MAIN_WINDOW_REVEAL_OFFSET_Y}")
        except Exception:
            self._reveal_target_y = None
        self.attributes("-alpha", MAIN_WINDOW_INITIAL_ALPHA)
        self.after(MAIN_WINDOW_REVEAL_DELAY_MS, self._fade_in)

    def _fade_in(self):
        try:
            alpha = float(self.attributes("-alpha"))
        except Exception:
            alpha = 1.0

        target_y = self._reveal_target_y
        if target_y is not None:
            try:
                current_y = int(self.winfo_y())
                if current_y > target_y:
                    step = min(MAIN_WINDOW_REVEAL_STEP_PX, current_y - target_y)
                    self.geometry(f"{self._app_w}x{self._app_h}+{int(self.winfo_x())}+{current_y - step}")
                else:
                    self._reveal_target_y = current_y
            except Exception:
                self._reveal_target_y = None

        if alpha < 1.0:
            self.attributes("-alpha", min(alpha + MAIN_WINDOW_FADE_IN_STEP, 1.0))
            self.after(MAIN_WINDOW_FADE_IN_INTERVAL_MS, self._fade_in)

    def _close_with_fade_out(self):
        try:
            for tp in self.tooltips.values():
                tp.cleanup()
        except Exception:
            pass
        try:
            self.status_panel.cleanup()
        except Exception:
            pass
        try:
            for dialog in self._dialog_cache.values():
                try:
                    if dialog.winfo_exists():
                        dialog.destroy()
                except Exception:
                    pass
        except Exception:
            pass

        alpha = self.attributes("-alpha")
        if alpha > 0:
            self.attributes("-alpha", max(alpha - MAIN_WINDOW_FADE_OUT_STEP, 0.0))
            self.after(MAIN_WINDOW_FADE_OUT_INTERVAL_MS, self._close_with_fade_out)
        else:
            self.destroy()

    def _tr(self, key: str, *args):
        entry = self.TRANSLATIONS.get(self.lang, self.TRANSLATIONS["es"]).get(key, f"<{key}>")
        if isinstance(entry, list):
            return random.choice(entry).format(*args)
        return entry.format(*args)

    def _build_atmosphere_image(self, size: tuple[int, int], theme: dict):
        width, height = size
        width = max(1, int(width))
        height = max(1, int(height))
        scale = 2
        W, H = width * scale, height * scale
        resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.LANCZOS)
        canvas = Image.new("RGBA", (W, H), with_alpha(theme["bg_base"], 255))
        is_light = self.current_theme == "Light"

        def add_ellipse(bounds, color, alpha, blur):
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(layer).ellipse(bounds, fill=with_alpha(color, alpha))
            layer = layer.filter(ImageFilter.GaussianBlur(max(1, int(blur))))
            canvas.alpha_composite(layer)

        def add_band(bounds, color, alpha, blur):
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            radius = max(1, int((bounds[3] - bounds[1]) * 0.52))
            ImageDraw.Draw(layer).rounded_rectangle(bounds, radius=radius, fill=with_alpha(color, alpha))
            layer = layer.filter(ImageFilter.GaussianBlur(max(1, int(blur))))
            canvas.alpha_composite(layer)

        top_color = theme["bg_elevated"] if is_light else theme["accent_blue"]
        bottom_color = theme["shadow_soft"] if is_light else theme["shadow_strong"]
        top_rgb = hex_to_rgb(top_color)
        bottom_rgb = hex_to_rgb(bottom_color)
        depth = Image.new("RGBA", (1, H), (0, 0, 0, 0))
        depth_pixels = depth.load()
        top_limit = 0.52 if is_light else 0.48
        bottom_start = 0.42 if is_light else 0.40
        top_alpha_strength = 6 if is_light else 5
        bottom_alpha_strength = 4 if is_light else 6

        for y in range(H):
            t = y / max(1, H - 1)
            top_alpha = int(max(0.0, 1.0 - (t / top_limit)) * top_alpha_strength) if t <= top_limit else 0
            bottom_alpha = int(max(0.0, (t - bottom_start) / max(0.001, 1.0 - bottom_start)) * bottom_alpha_strength) if t >= bottom_start else 0
            if bottom_alpha > top_alpha:
                depth_pixels[0, y] = (*bottom_rgb, bottom_alpha)
            else:
                depth_pixels[0, y] = (*top_rgb, top_alpha)

        canvas.alpha_composite(depth.resize((W, H), resample))

        if is_light:
            add_ellipse((int(W * 0.40), -int(H * 0.22), int(W * 1.14), int(H * 0.34)), theme["accent_blue"], 14, int(H * 0.22))
            add_ellipse((int(W * 0.56), -int(H * 0.24), int(W * 1.22), int(H * 0.30)), theme["accent_purple"], 15, int(H * 0.23))
            add_band((int(W * 0.68), -int(H * 0.04), int(W * 1.04), int(H * 0.18)), theme["bg_elevated"], 10, int(H * 0.16))
            add_ellipse((-int(W * 0.16), int(H * 0.34), int(W * 0.34), int(H * 0.82)), theme["accent_blue"], 8, int(H * 0.20))
            add_ellipse((-int(W * 0.10), int(H * 0.42), int(W * 0.30), int(H * 0.90)), theme["accent_purple"], 7, int(H * 0.18))
            add_band((-int(W * 0.02), int(H * 0.46), int(W * 0.18), int(H * 0.76)), theme["bg_elevated"], 7, int(H * 0.14))
        else:
            add_ellipse((int(W * 0.38), -int(H * 0.24), int(W * 1.14), int(H * 0.30)), theme["accent_blue"], 11, int(H * 0.24))
            add_ellipse((int(W * 0.56), -int(H * 0.24), int(W * 1.22), int(H * 0.28)), theme["accent_purple"], 11, int(H * 0.22))
            add_band((int(W * 0.70), -int(H * 0.02), int(W * 1.04), int(H * 0.18)), theme["glow_blue_soft"], 9, int(H * 0.16))
            add_ellipse((-int(W * 0.16), int(H * 0.34), int(W * 0.32), int(H * 0.86)), theme["glow_blue_soft"], 10, int(H * 0.24))
            add_ellipse((-int(W * 0.10), int(H * 0.42), int(W * 0.28), int(H * 0.92)), theme["glow_purple_soft"], 9, int(H * 0.22))
            add_band((-int(W * 0.02), int(H * 0.46), int(W * 0.18), int(H * 0.80)), theme["accent_blue"], 6, int(H * 0.15))

        return canvas.resize((width, height), resample)

    def _register_surface_backdrop(self, widget):
        try:
            label = tk.Label(widget, bd=0, highlightthickness=0)
            label.place(x=0, y=0, relwidth=1.0, relheight=1.0)
            label.lower()
            widget.bind("<Configure>", lambda event: self._schedule_background_refresh(), add="+")
            self._surface_backdrops[widget] = {"label": label, "photo": None}
        except Exception:
            pass

    def _refresh_surface_backdrops(self):
        theme = get_theme_tokens(self.current_theme)
        stale_widgets = []
        for widget, payload in self._surface_backdrops.items():
            try:
                label = payload.get("label")
                if not widget.winfo_exists() or label is None or not label.winfo_exists():
                    stale_widgets.append(widget)
                    continue
                patch, _ = self.get_backdrop_patch(widget)
                if patch is None:
                    payload["photo"] = None
                    label.configure(image="", bg=theme["bg_base"])
                else:
                    photo = ImageTk.PhotoImage(patch)
                    payload["photo"] = photo
                    label.configure(image=photo, bg=theme["bg_base"])
                label.place(x=0, y=0, relwidth=1.0, relheight=1.0)
                label.lower()
            except Exception:
                pass
        for widget in stale_widgets:
            self._surface_backdrops.pop(widget, None)

    def _refresh_background_dependents(self):
        try:
            if hasattr(self, "left_sidebar") and self.left_sidebar.winfo_exists():
                self.left_sidebar.refresh_backdrop()
        except Exception:
            pass
        try:
            if hasattr(self, "right_sidebar") and self.right_sidebar.winfo_exists():
                self.right_sidebar.refresh_backdrop()
        except Exception:
            pass
        try:
            if hasattr(self, "main_menu_frame") and self.main_menu_frame.winfo_exists():
                self.main_menu_frame.refresh_backdrop()
        except Exception:
            pass
        try:
            if hasattr(self, "status_panel") and self.status_panel.winfo_exists():
                self.status_panel.refresh_backdrop()
        except Exception:
            pass
        try:
            self._schedule_header_refresh()
        except Exception:
            pass

    def _mean_hex_from_patch(self, patch):
        try:
            theme = get_theme_tokens(self.current_theme)
            base = Image.new("RGBA", patch.size, with_alpha(theme["bg_base"], 255))
            merged = Image.alpha_composite(base, patch).convert("RGB")
            stat = ImageStat.Stat(merged)
            r, g, b = [max(0, min(255, int(round(x)))) for x in stat.mean[:3]]
            return f"#{r:02X}{g:02X}{b:02X}"
        except Exception:
            return get_theme_tokens(self.current_theme)["bg_base"]

    def _sample_backdrop_color(self, widget, *, width=None, height=None):
        patch, _ = self.get_backdrop_patch(widget, width=width, height=height)
        if patch is None:
            return get_theme_tokens(self.current_theme)["bg_base"]
        return self._mean_hex_from_patch(patch)

    def _refresh_local_surface_colors(self):
        theme = get_theme_tokens(self.current_theme)

        try:
            if hasattr(self, "main_menu_frame") and self.main_menu_frame.winfo_exists():
                self.main_menu_frame.configure(outside_bg=theme["bg_base"], fill_color=theme["bg_panel"], border_color=theme["border_subtle"], backdrop_provider=self.get_backdrop_patch)
        except Exception:
            pass

        try:
            if hasattr(self, "status_panel") and self.status_panel.winfo_exists():
                self.status_panel.set_backdrop_color(theme["bg_base"])
                self.status_panel.refresh_backdrop()
        except Exception:
            pass

        try:
            if hasattr(self, "header_frame") and self.header_frame.winfo_exists():
                self.header_frame.configure(bg=theme["bg_base"])
                self.header_canvas.configure(bg=theme["bg_base"])
                self._schedule_header_refresh()
        except Exception:
            pass

    def get_backdrop_patch(self, widget, width=None, height=None):
        if self._background_image is None:
            return None, None
        try:
            patch_width = max(1, int(width if width is not None else widget.winfo_width()))
            patch_height = max(1, int(height if height is not None else widget.winfo_height()))
            origin_x = int(widget.winfo_rootx() - self._background_canvas.winfo_rootx())
            origin_y = int(widget.winfo_rooty() - self._background_canvas.winfo_rooty())
        except Exception:
            return None, None

        patch = Image.new("RGBA", (patch_width, patch_height), with_alpha(get_theme_tokens(self.current_theme)["bg_base"], 255))
        source = self._background_image
        left = max(0, origin_x)
        top = max(0, origin_y)
        right = min(source.width, origin_x + patch_width)
        bottom = min(source.height, origin_y + patch_height)

        if right > left and bottom > top:
            crop = source.crop((left, top, right, bottom))
            paste_x = max(0, -origin_x)
            paste_y = max(0, -origin_y)
            patch.paste(crop, (paste_x, paste_y), crop)

        return patch, (self._background_revision, origin_x, origin_y, patch_width, patch_height)

    # =========================================================================
    # CONSTRUCCION DE UI
    # =========================================================================

    def _create_atmosphere_background(self):
        self._background_canvas = tk.Canvas(self, highlightthickness=0, bd=0, relief="flat")
        self._background_canvas.place(x=0, y=0, relwidth=1.0, relheight=1.0)
        self.tk.call("lower", self._background_canvas._w)
        self.bind("<Configure>", self._schedule_background_refresh, add="+")

    def _schedule_background_refresh(self, event=None):
        if event is not None and event.widget is not self:
            return
        if self._background_after_id is not None:
            try:
                self.after_cancel(self._background_after_id)
            except Exception:
                pass
        try:
            self._background_after_id = self.after(MAIN_WINDOW_BG_REFRESH_DELAY_MS, self._refresh_background_canvas)
        except Exception:
            self._background_after_id = None

    def _refresh_background_canvas(self):
        self._background_after_id = None
        try:
            width = max(1, int(self.winfo_width()))
            height = max(1, int(self.winfo_height()))
        except Exception:
            return

        theme = get_theme_tokens(self.current_theme)
        cache_key = (width, height, self.current_theme)
        background_changed = False

        try:
            if cache_key != self._background_cache_key or self._background_image is None or self._background_photo is None:
                self._background_image = self._build_atmosphere_image((width, height), theme)
                self._background_photo = ImageTk.PhotoImage(self._background_image)
                self._background_cache_key = cache_key
                self._background_revision += 1
                background_changed = True
        except Exception:
            self._background_image = None
            self._background_photo = None
            self._background_cache_key = None
            background_changed = True

        self._background_canvas.configure(bg=theme["bg_base"])
        self._background_canvas.delete("all")
        if self._background_photo is not None:
            self._background_canvas.create_image(0, 0, image=self._background_photo, anchor="nw")
        else:
            self._background_canvas.create_rectangle(0, 0, width + 1, height + 1, outline="", fill=theme["bg_base"])
        self.tk.call("lower", self._background_canvas._w)
        self._refresh_surface_backdrops()
        self._refresh_local_surface_colors()
        if background_changed:
            self._refresh_background_dependents()
        try:
            if hasattr(self, "footer_frame") and self.footer_frame.winfo_exists():
                self.footer_frame.lift()
        except Exception:
            pass

    def _build_ui(self):
        self._create_atmosphere_background()
        theme_keys = get_theme_tokens(self.current_theme)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        footer_clearance = max(0, MAIN_WINDOW_FOOTER_HEIGHT - 35)

        self.left_container = tk.Frame(self, bg=theme_keys["bg_base"], bd=0, highlightthickness=0)
        self.left_container.grid(row=0, column=0, sticky="ns", padx=MAIN_WINDOW_SIDE_PADX, pady=(MAIN_WINDOW_LEFT_PADY[0], MAIN_WINDOW_LEFT_PADY[1] + footer_clearance))
        self._register_surface_backdrop(self.left_container)

        self.right_container = tk.Frame(self, bg=theme_keys["bg_base"], bd=0, highlightthickness=0)
        self.right_container.grid(row=0, column=2, sticky="ns", padx=MAIN_WINDOW_SIDE_PADX, pady=(MAIN_WINDOW_RIGHT_PADY[0], MAIN_WINDOW_RIGHT_PADY[1] + footer_clearance))
        self._register_surface_backdrop(self.right_container)

        self.center_container = tk.Frame(self, bg=theme_keys["bg_base"], bd=0, highlightthickness=0)
        self.center_container.grid(row=0, column=1, sticky="nsew", pady=(MAIN_WINDOW_CENTER_PADY[0], MAIN_WINDOW_CENTER_PADY[1] + footer_clearance))
        self.center_container.grid_columnconfigure(0, weight=1)
        self.center_container.grid_rowconfigure(3, weight=1)
        self._register_surface_backdrop(self.center_container)

        self._create_header(self.center_container)
        self._create_main_buttons(self.center_container)
        self._create_status_area(self.center_container)

        self.left_sidebar = LeftSidebar(self.left_container, text=f"{APP_DISPLAY_NAME} v{VERSION}", backdrop_provider=self.get_backdrop_patch)
        self.right_sidebar = RightSidebar(self.right_container, icons=self.icons, current_theme=self.current_theme, backdrop_provider=self.get_backdrop_patch)
        self._register_surface_backdrop(self.right_sidebar)
        self._register_surface_backdrop(self.right_sidebar._button_container)
        self._register_surface_backdrop(self.status_panel)
        self.sidebar_buttons = self.right_sidebar.buttons

        self._create_footer()

    def _create_header(self, parent):
        theme_keys = get_theme_tokens(self.current_theme)
        logo = self._get_header_logo_image()
        logo_height = 0 if logo is None else int(logo.height)
        header_height = max(72, logo_height + MAIN_WINDOW_GREETING_FONT_SIZE + 24)

        self.header_frame = tk.Frame(parent, bg=theme_keys["bg_base"], bd=0, highlightthickness=0, height=header_height)
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=MAIN_WINDOW_HEADER_PADY)
        self.header_frame.grid_propagate(False)

        self.header_canvas = tk.Canvas(self.header_frame, height=header_height, highlightthickness=0, bd=0, relief="flat", bg=theme_keys["bg_base"])
        self.header_canvas.pack(fill="both", expand=True)
        self.header_frame.bind("<Configure>", self._schedule_header_refresh, add="+")
        self.header_canvas.bind("<Configure>", self._schedule_header_refresh, add="+")

    def _create_main_buttons(self, parent):
        theme_keys = get_theme_tokens(self.current_theme)

        self.main_menu_frame = BlendedRoundedFrame(
            parent,
            outside_bg=theme_keys["bg_base"],
            fill_color=theme_keys["bg_panel"],
            corner_radius=MAIN_WINDOW_MAIN_MENU_RADIUS,
            border_width=MAIN_WINDOW_MAIN_MENU_BORDER_WIDTH,
            border_color=theme_keys["border_subtle"],
            content_inset=max(8, MAIN_WINDOW_MAIN_MENU_RADIUS // 2),
            backdrop_provider=self.get_backdrop_patch
        )
        self.main_menu_frame.grid(row=1, column=0, sticky="ew", pady=(0, MAIN_WINDOW_MAIN_MENU_BOTTOM_GAP))

        self.main_buttons_frame = ctk.CTkFrame(self.main_menu_frame.content_frame, fg_color="transparent", bg_color="transparent")
        self.main_buttons_frame.pack(pady=MAIN_WINDOW_MAIN_MENU_PAD, padx=MAIN_WINDOW_MAIN_MENU_PAD)

        outside_bg = theme_keys["bg_panel"]
        btn_blue = get_button_tokens("blue")
        btn_green = get_button_tokens("green")
        btn_red = get_button_tokens("red")

        common = {
            "width": BTN_W_MAIN,
            "height": BTN_H_MAIN,
            "outside_bg": outside_bg,
            "border_width": MAIN_WINDOW_BUTTON_BORDER_WIDTH,
            "font": (FONT_FAMILY_PRIMARY, MAIN_WINDOW_BUTTON_FONT_SIZE, "bold"),
            "text_color": btn_blue["text"],
        }

        def build_palette(palette):
            return {
                "fg_color": palette["bg"],
                "hover_color": palette["hover"],
                "border_color": palette["border"],
                "gradient_start": palette.get("gradient_start"),
                "gradient_mid": palette.get("gradient_mid"),
                "gradient_end": palette.get("gradient_end"),
                "hover_gradient_start": palette.get("hover_gradient_start"),
                "hover_gradient_mid": palette.get("hover_gradient_mid"),
                "hover_gradient_end": palette.get("hover_gradient_end"),
            }

        self.main_buttons = {
            "selpath": PillTextButton(self.main_buttons_frame, **build_palette(btn_blue), **common),
            "choose": PillTextButton(self.main_buttons_frame, **build_palette(btn_blue), **common),
            "create_tree": PillTextButton(self.main_buttons_frame, **build_palette(btn_blue), **common),
            "openlect": PillTextButton(self.main_buttons_frame, **build_palette(btn_blue), **common),
            "openlast": PillTextButton(self.main_buttons_frame, **build_palette(btn_green), **common),
            "delete": PillTextButton(self.main_buttons_frame, **build_palette(btn_red), **common),
        }

        BTN_SPACING = MAIN_WINDOW_BUTTON_SPACING
        for btn in self.main_buttons.values():
            btn.pack(pady=BTN_SPACING, anchor="center")

    def _create_status_area(self, parent):
        theme_keys = get_theme_tokens(self.current_theme)
        self.progress_frame = tk.Frame(parent, bg=theme_keys["bg_base"], bd=0, highlightthickness=0)
        self.progress_frame.grid(row=2, column=0, sticky="nsew", pady=MAIN_WINDOW_STATUS_AREA_PADY)
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self._register_surface_backdrop(self.progress_frame)

        self.status_panel = StatusPanel(self.progress_frame, min_visible_seconds=MAIN_WINDOW_STATUS_MIN_VISIBLE_SECONDS)
        self.status_panel.grid(row=0, column=0, sticky="ew")
        self.status_panel.set_backdrop_provider(self.get_backdrop_patch)

        self.btn_cancel = self.status_panel.btn_cancel

    def _create_footer(self):
        theme_keys = get_theme_tokens(self.current_theme)
        self.footer_frame = tk.Frame(self, height=MAIN_WINDOW_FOOTER_HEIGHT, bg=theme_keys["bg_footer"], bd=0, highlightthickness=0)
        self.footer_frame.pack_propagate(False)

        self.footer_frame.place(relx=0.0, rely=1.0, anchor="sw", relwidth=1.0)
        self.footer_frame.lift()

        self.footer_line = ctk.CTkFrame(self.footer_frame, height=MAIN_WINDOW_FOOTER_LINE_HEIGHT, corner_radius=0, bg_color=theme_keys["bg_footer"])
        self.footer_line.pack(side="top", fill="x")

        self.lbl_copyright = ctk.CTkLabel(
            self.footer_frame,
            text="",
            font=(FONT_FAMILY_PRIMARY, MAIN_WINDOW_FOOTER_FONT_SIZE),
            fg_color="transparent",
            bg_color=theme_keys["bg_footer"]
        )
        self.lbl_copyright.place(relx=0.5, rely=0.5, anchor="center")

    # =========================================================================
    # LOGICA DE ACTUALIZACION VISUAL
    # =========================================================================

    def update_ui_texts(self):
        hour = datetime.datetime.now().hour
        greet_key = "greet_m" if 5 <= hour < 12 else "greet_a" if 12 <= hour < 19 else "greet_n"
        try:
            user = os.getlogin().lower().capitalize()
        except OSError:
            user = self._tr("fallback_user") if hasattr(self, "_tr") else translate_default("fallback_user")
        self._header_greeting_text = f"{self._tr(greet_key)} {user}{self._tr('welcome')}"
        self._schedule_header_refresh()

        key_map = {
            "selpath": "btn_sel_lecturas",
            "choose": "btn_choose_folder",
            "create_tree": "btn_create_tree",
            "openlect": "btn_open_lecturas",
            "openlast": "btn_open_last",
            "delete": "btn_del",
        }

        for key, btn in self.main_buttons.items():
            if key in key_map:
                btn.configure(text=self._tr(key_map[key]))

        self.status_panel.set_translator(lambda k: self._tr(k))
        self.lbl_copyright.configure(text=self._tr("footer_copyright", YEAR, AUTHOR))

        tooltip_map = {
            "ver": "tooltip_ver",
            "nover": "tooltip_nover",
            "etiqueta": "tooltip_etiqueta",
            "theme_icon": "tooltip_tema",
            "traducir": "tooltip_idioma",
            "restaurar": "tooltip_restaurar",
            "perfil": "tooltip_perfil",
            "github": "tooltip_github",
            "info": "tooltip_info",
            "ajustes": "tooltip_ajustes",
        }

        for key, btn in self.sidebar_buttons.items():
            if key in tooltip_map:
                txt = self._tr(tooltip_map[key])
                if key in self.tooltips:
                    self.tooltips[key].text = txt
                else:
                    self.tooltips[key] = CustomTooltip(btn, text=txt)

        try:
            for dialog in self._dialog_cache.values():
                try:
                    if dialog.winfo_exists() and hasattr(dialog, "refresh_texts"):
                        dialog.refresh_texts()
                except Exception:
                    pass
        except Exception:
            pass

        try:
            self._refresh_local_surface_colors()
        except Exception:
            pass

    def apply_theme(self):
        ctk.set_appearance_mode(self.current_theme)

        theme_keys = get_theme_tokens(self.current_theme)

        self.configure(fg_color=theme_keys["bg_base"])

        self.left_sidebar.apply_theme(self.current_theme)
        self.right_sidebar.apply_theme(self.current_theme)
        self.status_panel.apply_theme(self.current_theme)

        try:
            self.left_container.configure(bg=theme_keys["bg_base"])
            self.right_container.configure(bg=theme_keys["bg_base"])
            self.center_container.configure(bg=theme_keys["bg_base"])
            self.header_frame.configure(bg=theme_keys["bg_base"])
            self.header_canvas.configure(bg=theme_keys["bg_base"])
            self.progress_frame.configure(bg=theme_keys["bg_base"])
            self.main_menu_frame.configure(outside_bg=theme_keys["bg_base"], fill_color=theme_keys["bg_panel"], border_color=theme_keys["border_subtle"], backdrop_provider=self.get_backdrop_patch)
            self.main_buttons_frame.configure(bg_color="transparent")
        except Exception:
            pass

        for btn in self.main_buttons.values():
            try:
                btn.configure(outside_bg=theme_keys["bg_panel"])
            except Exception:
                pass

        try:
            self.footer_frame.configure(bg=theme_keys["bg_footer"])
            self.footer_line.configure(bg_color=theme_keys["bg_footer"], fg_color=theme_keys["separator_line"])
            self.lbl_copyright.configure(bg_color=theme_keys["bg_footer"], fg_color="transparent", text_color=theme_keys["text_secondary"])
        except Exception:
            pass

        self._refresh_background_canvas()
        self._schedule_header_refresh()

    def switch_theme_animated(self, new_theme: str):
        if new_theme == self.current_theme or self._is_theme_switching:
            return
        self._is_theme_switching = True
        self._pending_new_theme = new_theme
        self._reveal_target_y = None
        CustomTooltip.hide_global()
        self._fade_out_for_switch()

    def _fade_out_for_switch(self):
        try:
            alpha = float(self.attributes("-alpha"))
            if alpha > 0.0:
                self.attributes("-alpha", max(alpha - MAIN_WINDOW_SWITCH_FADE_OUT_STEP, 0.0))
                self.after(MAIN_WINDOW_SWITCH_FADE_OUT_INTERVAL_MS, self._fade_out_for_switch)
            else:
                try:
                    self.withdraw()
                except Exception:
                    pass
                self.after(MAIN_WINDOW_SWITCH_HOLD_MS, self._apply_theme_after_switch)
        except Exception:
            self._is_theme_switching = False
            self.current_theme = self._pending_new_theme
            self.apply_theme()
            self.attributes("-alpha", 1.0)

    def _apply_theme_after_switch(self):
        try:
            self.current_theme = self._pending_new_theme
            self.apply_theme()
            self.update_idletasks()
            self.attributes("-alpha", 0.0)
            self.after(MAIN_WINDOW_SWITCH_REBUILD_DELAY_MS, self._reveal_after_theme_switch)
        except Exception:
            self._is_theme_switching = False
            try:
                self.deiconify()
            except Exception:
                pass
            self.attributes("-alpha", 1.0)

    def _reveal_after_theme_switch(self):
        try:
            self._restore_window_stack_after_theme_switch()
            self.attributes("-alpha", 0.0)
            self._fade_in_after_switch()
        except Exception:
            self._is_theme_switching = False
            self.attributes("-alpha", 1.0)

    def _restore_window_stack_after_theme_switch(self):
        try:
            self.deiconify()
        except Exception:
            pass
        try:
            self.lift()
        except Exception:
            pass
        try:
            self.focus_force()
        except Exception:
            pass
        try:
            self.attributes("-topmost", True)
            self.after(MAIN_WINDOW_TOPMOST_RESET_DELAY_MS, lambda: self.attributes("-topmost", False))
        except Exception:
            pass

    def _fade_in_after_switch(self):
        try:
            alpha = float(self.attributes("-alpha"))
        except Exception:
            alpha = 1.0

        if alpha < 1.0:
            self.attributes("-alpha", min(alpha + MAIN_WINDOW_SWITCH_FADE_IN_STEP, 1.0))
            self.after(MAIN_WINDOW_SWITCH_FADE_IN_INTERVAL_MS, self._fade_in_after_switch)
        else:
            self._is_theme_switching = False

    def switch_profile_animated(self, apply_callback, complete_callback=None):
        if self._is_theme_switching or self._is_profile_switching:
            return
        self._is_profile_switching = True
        self._profile_switch_apply_callback = apply_callback
        self._profile_switch_complete_callback = complete_callback
        self._reveal_target_y = None
        CustomTooltip.hide_global()
        self._fade_out_for_profile_switch()

    def _fade_out_for_profile_switch(self):
        try:
            alpha = float(self.attributes("-alpha"))
            if alpha > 0.0:
                self.attributes("-alpha", max(alpha - MAIN_WINDOW_SWITCH_FADE_OUT_STEP, 0.0))
                self.after(MAIN_WINDOW_SWITCH_FADE_OUT_INTERVAL_MS, self._fade_out_for_profile_switch)
            else:
                self.after(MAIN_WINDOW_SWITCH_HOLD_MS, self._apply_profile_after_switch)
        except Exception:
            self._finish_profile_switch_immediately()

    def _apply_profile_after_switch(self):
        try:
            if callable(self._profile_switch_apply_callback):
                self._profile_switch_apply_callback()
            self.update_idletasks()
            self._restore_window_stack_after_theme_switch()
            self.attributes("-alpha", 0.0)
            self._fade_in_after_profile_switch()
        except Exception:
            self._finish_profile_switch_immediately()

    def _fade_in_after_profile_switch(self):
        try:
            alpha = float(self.attributes("-alpha"))
        except Exception:
            alpha = 1.0

        if alpha < 1.0:
            self.attributes("-alpha", min(alpha + MAIN_WINDOW_SWITCH_FADE_IN_STEP, 1.0))
            self.after(MAIN_WINDOW_SWITCH_FADE_IN_INTERVAL_MS, self._fade_in_after_profile_switch)
        else:
            self._is_profile_switching = False
            callback = self._profile_switch_complete_callback
            self._profile_switch_apply_callback = None
            self._profile_switch_complete_callback = None
            if callable(callback):
                self.after(100, callback)

    def _finish_profile_switch_immediately(self):
        self._is_profile_switching = False
        apply_callback = self._profile_switch_apply_callback
        complete_callback = self._profile_switch_complete_callback
        self._profile_switch_apply_callback = None
        self._profile_switch_complete_callback = None
        try:
            if callable(apply_callback):
                apply_callback()
        except Exception:
            pass
        try:
            self.attributes("-alpha", 1.0)
        except Exception:
            pass
        if callable(complete_callback):
            self.after(100, complete_callback)

    def prepare_soft_refresh(self):
        CustomTooltip.hide_global()
        try:
            current_alpha = float(self.attributes("-alpha"))
        except Exception:
            current_alpha = 1.0
        try:
            self.attributes("-alpha", min(current_alpha, MAIN_WINDOW_SOFT_REFRESH_ALPHA))
        except Exception:
            pass
        self._reveal_target_y = None

    def complete_soft_refresh(self):
        self._fade_in()

    def _create_view_dialog(self):
        return TagsConfigDialog(
            parent=self,
            title=self._tr("dlg_ver_title"),
            folders_prompt=self._tr("dlg_ver_folder_prompt"),
            initial_folders=self.controller.config.get("etiquetas_carpetas_importantes", []),
            files_prompt=self._tr("dlg_ver_file_prompt"),
            initial_files=self.controller.config.get("etiquetas_extensiones_incluidas", []),
            allow_autodetect=True,
            excluded_folders=self.controller.config.get("etiquetas_carpetas_excluidas", []),
            excluded_files=self.controller.config.get("etiquetas_archivos_excluidos", []),
            media_extensions=self.controller.config.get("media_extensions", []),
            persistent=True,
            defer_show=True
        )

    def _create_no_view_dialog(self):
        return TagsConfigDialog(
            parent=self,
            title=self._tr("dlg_nover_title"),
            folders_prompt=self._tr("dlg_nover_folder_prompt"),
            initial_folders=self.controller.config.get("etiquetas_carpetas_excluidas", []),
            files_prompt=self._tr("dlg_nover_file_prompt"),
            initial_files=self.controller.config.get("etiquetas_archivos_excluidos", []),
            extra_checkbox_text=self._tr("chk_use_gitignore"),
            extra_checkbox_value=self.controller.config.get("use_gitignore_exclusions", False),
            persistent=True,
            defer_show=True
        )

    def _create_media_dialog(self):
        tags_stored = self.controller.config.get("etiquetas_multimedia_config", [])
        if not tags_stored:
            raw_exts = self.controller.config.get("media_extensions", [])
            current_files = [{"nombre": x, "estado": "activo"} for x in raw_exts]
        else:
            current_files = tags_stored
        view_exts = {t["nombre"] for t in self.controller.config.get("etiquetas_extensiones_incluidas", [])}
        no_view_items = {t["nombre"] for t in self.controller.config.get("etiquetas_archivos_excluidos", [])}
        return TagsConfigDialog(
            parent=self,
            title=self._tr("dlg_etiqueta_title"),
            folders_prompt=None,
            initial_folders=None,
            files_prompt=self._tr("dlg_etiqueta_file_prompt"),
            initial_files=current_files,
            forbidden_items=view_exts.union(no_view_items),
            persistent=True,
            defer_show=True
        )

    def _create_profiles_dialog(self):
        profiles = self.controller.config.get("_profiles_meta", {})
        active_id = self.controller.config.get("_active_profile_id", "default")
        if not profiles:
            profiles = {"default": self.controller.config.copy()}
        return ProfilesDialog(
            parent=self,
            profiles_meta=profiles,
            active_id=active_id,
            persistent=True,
            defer_show=True
        )

    def _create_settings_dialog(self):
        return SettingsDialog(
            parent=self,
            current_extension=self.controller.config.get("report_extension", ".txt"),
            current_exe_path=self.controller.config.get("custom_exe_path", ""),
            persistent=True,
            defer_show=True
        )

    def _get_or_create_dialog(self, key, factory):
        dialog = self._dialog_cache.get(key)
        if dialog is None:
            dialog = factory()
            self._dialog_cache[key] = dialog
        else:
            try:
                if not dialog.winfo_exists():
                    dialog = factory()
                    self._dialog_cache[key] = dialog
            except Exception:
                dialog = factory()
                self._dialog_cache[key] = dialog
        return dialog

    def _preload_persistent_dialogs(self):
        try:
            self.get_view_dialog()
            self.get_no_view_dialog()
            self.get_media_dialog()
            self.get_profiles_dialog()
            self.get_settings_dialog()
        except Exception:
            pass

    def get_view_dialog(self):
        return self._get_or_create_dialog("view", self._create_view_dialog)

    def get_no_view_dialog(self):
        return self._get_or_create_dialog("no_view", self._create_no_view_dialog)

    def get_media_dialog(self):
        return self._get_or_create_dialog("media", self._create_media_dialog)

    def get_profiles_dialog(self):
        return self._get_or_create_dialog("profiles", self._create_profiles_dialog)

    def get_settings_dialog(self):
        return self._get_or_create_dialog("settings", self._create_settings_dialog)


    # =========================================================================
    # ESTADO Y CONTROL
    # =========================================================================


    def _cancel_modal_fail_safe(self):
        if self._modal_fail_safe_after_id:
            try:
                self.after_cancel(self._modal_fail_safe_after_id)
            except Exception:
                pass
        self._modal_fail_safe_after_id = None

    def _schedule_modal_fail_safe(self):
        self._cancel_modal_fail_safe()
        try:
            self._modal_fail_safe_after_id = self.after(MAIN_WINDOW_MODAL_FAIL_SAFE_DELAY_MS, self._modal_fail_safe_check)
        except Exception:
            self._modal_fail_safe_after_id = None

    def _has_live_modal_dialog(self) -> bool:
        try:
            for child in self.winfo_children():
                try:
                    if not getattr(child, "_is_base_dialog", False):
                        continue
                    if not child.winfo_exists():
                        continue
                    if str(child.state()) == "withdrawn":
                        continue
                    return True
                except Exception:
                    pass
        except Exception:
            pass
        return False

    def _modal_fail_safe_check(self):
        self._modal_fail_safe_after_id = None
        if not self._is_modal_open:
            return
        if self._has_live_modal_dialog():
            self._schedule_modal_fail_safe()
            return
        self.restore_ui_from_modal()

    def get_min_visible_completion_delay_ms(self) -> int:
        return self.status_panel.get_min_visible_completion_delay_ms()

    def set_progress(self, percentage, file_context=None):
        self.status_panel.set_progress(percentage, file_context)

    def toggle_ui_for_processing(self, is_active: bool, mode: str = "determinate", text: str = None,
                                 final_status: str = None):
        CustomTooltip.hide_global()
        if self._is_modal_open:
            return

        state = "disabled" if is_active else "normal"
        for btn in self.main_buttons.values():
            btn.configure(state=state)
        for btn in self.sidebar_buttons.values():
            btn.configure(state=state)

        self.left_sidebar.configure(state=state)
        self.status_panel.set_active(is_active, mode=mode, text=text, final_status=final_status)

    def dim_ui_for_modal(self):
        CustomTooltip.hide_global()
        self._is_modal_open = True
        for btn in self.main_buttons.values():
            btn.configure(state="disabled")
        for btn in self.sidebar_buttons.values():
            btn.configure(state="disabled")
        self.left_sidebar.configure(state="disabled")
        self._schedule_modal_fail_safe()

    def restore_ui_from_modal(self):
        CustomTooltip.hide_global()
        self._cancel_modal_fail_safe()
        self._is_modal_open = False
        if not self.controller.is_processing:
            for btn in self.main_buttons.values():
                btn.configure(state="normal")
            for btn in self.sidebar_buttons.values():
                btn.configure(state="normal")
            self.left_sidebar.configure(state="normal")
        else:
            pass

    def show_message(self, title_key: str, message_key: str, *args):
        CustomTooltip.hide_global()
        try:
            def _on_message_closed():
                try:
                    if getattr(self.status_panel, "_mode", "") == "done":
                        self.status_panel.back_to_idle()
                except Exception:
                    pass
            MessageDialog(self, self._tr(title_key), self._tr(message_key, *args), on_close=_on_message_closed)
        except Exception:
            self.restore_ui_from_modal()

    def show_app_info(self):
        if self.controller and hasattr(self.controller, "open_manual_link"):
            self.controller.open_manual_link()
        else:
            webbrowser.open(APP_WEBSITE_URL)


